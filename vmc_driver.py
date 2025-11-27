import time
import threading
import queue
import serial
from vmc_codes import *

class VMCDriver:
    def __init__(self, port, baudrate=57600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        # --- SHARED STATE ---
        self.running = False
        self.packet_number = 1  # Valid range: 1-255
        
        # This holds the command we WANT to send.
        # Format: {'cmd': 0x00, 'data': [], 'retries': 0, 'expect_response': None}
        self.pending_command = None
        
        # This holds the response we received from the VMC
        self.last_response = None
        
        # Events for Thread Synchronization
        self.evt_response_ready = threading.Event() # Set when VMC replies
        self.lock = threading.Lock() # Protects shared variables
        
        # Unsolicited Data Queue (Money received, Errors pushed by VMC)
        self.async_events = queue.Queue()

    def start(self):
        """Starts the Serial Thread"""
        self.running = True
        self.serial = serial.Serial(
            self.port, 
            self.baudrate, 
            timeout=None # Blocking read for efficiency
        )
        self.thread = threading.Thread(target=self._serial_loop, daemon=True)
        self.thread.start()
        print(f"[VMC] Driver started on {self.port}")
        
        # Rule 8: Startup Sync (Queue this immediately)
        self.send_command_nowait(CMD_SEND["REQUEST_INFO_SYNC"], [])

    def calculate_xor(self, packet):
        """Calculates XOR from STX to end of payload (PDF Section 3)"""
        xor = 0x00
        for byte in packet:
            xor ^= byte
        return xor

    def build_packet(self, cmd_byte, data_bytes, pack_no):
        """Constructs the raw byte array to send"""
        # Protocol: STX(2) + CMD(1) + LEN(1) + [PackNO(1) + Data(n)] + XOR(1)
        length_byte = 1 + len(data_bytes) # 1 for PackNO + Data
        
        # Determine payload based on command type
        if cmd_byte == CMD_ACK:
            # ACKs are special: FA FB 42 00 43 (No PackNO, Len=0)
            packet = STX + [cmd_byte, 0x00]
        else:
            packet = STX + [cmd_byte, length_byte, pack_no] + list(data_bytes)
            
        xor = self.calculate_xor(packet)
        packet.append(xor)
        return bytearray(packet)

    def send_command_blocking(self, cmd_byte, data_bytes=[], timeout=5.0):
        """
        API CALL: Sends a command and BLOCKS until response or timeout.
        Implements 'One thing at a time' rule.
        """
        with self.lock:
            # 1. Setup the pending command
            expect_code = EXPECTED_RESPONSES.get(cmd_byte, None)
            
            self.pending_command = {
                'cmd': cmd_byte,
                'data': data_bytes,
                'retries': 0,
                'sent_status': 'WAITING_FOR_POLL',
                'expect_code': expect_code
            }
            
            self.last_response = None
            self.evt_response_ready.clear()
            
        print(f"[API] Queued Command {hex(cmd_byte)}. Waiting for VMC...")
        
        # 2. Wait for the Serial Thread to do the work
        success = self.evt_response_ready.wait(timeout=timeout)
        
        with self.lock:
            result = self.last_response
            # Cleanup
            self.pending_command = None
            
        if not success:
            print("[API] Error: Timeout waiting for VMC response")
            return {"error": "TIMEOUT"}
            
        return result

    def send_command_nowait(self, cmd_byte, data_bytes=[]):
        """Internal use: Queue a command without waiting (e.g. startup sync)"""
        with self.lock:
            self.pending_command = {
                'cmd': cmd_byte,
                'data': data_bytes,
                'retries': 0,
                'sent_status': 'WAITING_FOR_POLL',
                'expect_code': EXPECTED_RESPONSES.get(cmd_byte, None)
            }

    def _serial_loop(self):
        """Main Loop: Handles POLL, ACKs, and Data parsing"""
        buffer = []
        
        while self.running:
            # A. READ ONE BYTE
            if self.serial.in_waiting > 0:
                byte = ord(self.serial.read(1))
                buffer.append(byte)
                
                # B. CHECK HEADER (FA FB)
                if len(buffer) >= 2:
                    if buffer[-2] == 0xFA and buffer[-1] == 0xFB:
                        # Found Start! Reset buffer to just these 2 bytes
                        buffer = [0xFA, 0xFB]
                        
                # C. PARSE PACKET
                # Min length is 5 (STX+CMD+LEN+XOR)
                if len(buffer) >= 5:
                    cmd_id = buffer[2]
                    data_len = buffer[3]
                    
                    # Full packet length = 4 header bytes + data_len + 1 XOR
                    expected_len = 4 + data_len + 1
                    
                    if len(buffer) >= expected_len:
                        # Full packet received!
                        self._process_incoming_packet(buffer)
                        buffer = [] # Clear for next packet

    def _process_incoming_packet(self, packet):
        """Decides what to do with the valid packet from VMC"""
        cmd_id = packet[2]
        
        # --- CASE 1: POLL (0x41) ---
        if cmd_id == CMD_POLL:
            self._handle_poll()

        # --- CASE 2: ACK (0x42) ---
        elif cmd_id == CMD_ACK:
            self._handle_ack()

        # --- CASE 3: DATA / RESPONSE ---
        else:
            self._handle_data_packet(packet)

    def _handle_poll(self):
        """VMC asked 'Do you have commands?'"""
        # Default action is to send ACK (Idle)
        send_ack = True

        if self.pending_command:
            status = self.pending_command['sent_status']
            
            # STATE 1: WAITING_FOR_POLL or SENT_WAITING_FOR_ACK
            # We have a command that needs to be sent (or resent if lost)
            if status == 'WAITING_FOR_POLL' or status == 'SENT_WAITING_FOR_ACK':
                if self.pending_command['retries'] >= 5:
                    print("[Driver] Command failed 5 times. Terminating.")
                    with self.lock:
                        self.last_response = {"error": "MAX_RETRIES_REACHED"}
                        self.evt_response_ready.set()
                        # Do not clear pending_command here, logic continues to send ACK
                    # send_ack remains True
                else:
                    # SEND THE COMMAND
                    cmd = self.pending_command['cmd']
                    data = self.pending_command['data']
                    
                    raw_packet = self.build_packet(cmd, data, self.packet_number)
                    self.serial.write(raw_packet)
                    
                    self.pending_command['sent_status'] = 'SENT_WAITING_FOR_ACK'
                    self.pending_command['retries'] += 1
                    
                    # Log the sent command so we know it went out!
                    print(f"[Driver] Sent Command {hex(cmd)} (Attempt {self.pending_command['retries']})")
                    
                    send_ack = False # We sent data, so don't send ACK
            
            # STATE 2: ACK_RECEIVED
            # We already sent command and VMC said "OK". 
            # We are now just waiting for the Data Packet (e.g. Dispense Result).
            elif status == 'ACK_RECEIVED':
                send_ack = True 

        # If no command logic took over, send the standard Idle ACK
        if send_ack:
            self.serial.write(self.build_packet(CMD_ACK, [], 0))

    def _handle_ack(self):
        """We received an ACK from VMC"""
        if self.pending_command and self.pending_command['sent_status'] == 'SENT_WAITING_FOR_ACK':
            # Great! VMC got our command.
            self.pending_command['sent_status'] = 'ACK_RECEIVED'
            
            # Rule 6: Increment Packet Number on success
            self.packet_number += 1
            if self.packet_number > 255: self.packet_number = 1
            
            # Does this command expect data?
            if self.pending_command['expect_code'] is None:
                # No data expected (e.g. Set Price). We are done!
                with self.lock:
                    self.last_response = {"status": "SUCCESS_ACK_ONLY"}
                    self.evt_response_ready.set()
            else:
                # We must wait for the data packet (Process 3)
                pass

    def _handle_data_packet(self, packet):
        """Process actual data (Inventory report, Dispense result, etc)"""
        cmd_id = packet[2]
        data_len = packet[3]
        
        # Extract Payload
        # Packet: STX(2) Cmd(1) Len(1) [PackNo(1) Payload(n-1)] Xor(1)
        if data_len > 0:
            vmc_pack_no = packet[4]
            payload = packet[5:-1]
        else:
            payload = []

        # 1. ALWAYS Send ACK back immediately (Process 3 Rule)
        self.serial.write(self.build_packet(CMD_ACK, [], 0))
        
        # 2. Check if this is the response we are waiting for
        is_expected = False
        if self.pending_command and self.pending_command['expect_code'] == cmd_id:
            with self.lock:
                self.last_response = {
                    "cmd": hex(cmd_id),
                    "data_hex": [hex(x) for x in payload],
                    "raw_data": list(payload)
                }
                self.evt_response_ready.set() # Wake up API
            is_expected = True
            
        # 3. If it's unsolicited data (Money in, Error), log or queue it
        if not is_expected:
            print(f"[Async] Received Event {hex(cmd_id)}: {list(payload)}")
            self.async_events.put({"cmd": cmd_id, "data": payload})
            
            # Also increment packet number for unsolicited successful transactions?
            # PDF implies PackNO increments on "correct completion". 
            # If we ACK'd their data, we should probably increment.
            self.packet_number += 1
            if self.packet_number > 255: self.packet_number = 1