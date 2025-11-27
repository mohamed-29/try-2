from flask import Flask, request, jsonify
from vmc_driver import VMCDriver
from vmc_codes import CMD_SEND, MENU_SUB_COMMANDS
import time

app = Flask(__name__)

# CONFIGURATION
# Update this to match your actual serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
SERIAL_PORT = '/dev/ttyS1' 
vmc = VMCDriver(port=SERIAL_PORT)

# --- GENERIC HELPERS ---
def int_to_bytes(value, length):
    """Helper to convert int to big-endian bytes"""
    return value.to_bytes(length, byteorder='big')

# --- ENDPOINTS ---

@app.route('/status', methods=['GET'])
def get_status():
    """Checks machine status (0x53)"""
    # 0x53 has no payload
    result = vmc.send_command_blocking(CMD_SEND["REQUEST_STATUS_SIMPLE"], [])
    return jsonify(result)

@app.route('/dispense', methods=['POST'])
def dispense():
    """Dispense Item (0x03)"""
    slot_id = request.json.get('slot_id') # e.g., 10
    
    # Payload: 2 bytes for Selection Number
    payload = int_to_bytes(slot_id, 2)
    
    result = vmc.send_command_blocking(CMD_SEND["DISPENSE_ITEM"], payload)
    
    # Parse specific logic here if needed, or return raw
    return jsonify(result)

@app.route('/price', methods=['POST'])
def set_price():
    """Set Price (0x12) - Example of sending Command -> ACK only"""
    slot_id = request.json.get('slot_id')
    price = request.json.get('price') # Integer cents
    
    # Payload: Slot(2) + Price(4)
    payload = int_to_bytes(slot_id, 2) + int_to_bytes(price, 4)
    
    result = vmc.send_command_blocking(CMD_SEND["SET_PRICE"], payload)
    return jsonify(result)

@app.route('/menu', methods=['POST'])
def menu_command():
    """
    Generic endpoint for all 0x70 Menu settings.
    Usage: {"sub_cmd": "TEMP_CONTROLLER_SETTING", "params": [1, 2, 3]}
    """
    sub_cmd_name = request.json.get('sub_cmd')
    params = request.json.get('params', []) # List of ints
    
    if sub_cmd_name not in MENU_SUB_COMMANDS:
        return jsonify({"error": "Unknown Sub Command"}), 400
        
    sub_cmd_byte = MENU_SUB_COMMANDS[sub_cmd_name]
    
    # Payload for 0x70 is: [SubCmdByte] + [Params...]
    payload = [sub_cmd_byte] + params
    
    result = vmc.send_command_blocking(CMD_SEND["MENU_COMMAND_WRAPPER"], payload)
    return jsonify(result)

@app.route('/events', methods=['GET'])
def get_async_events():
    """Fetch unsolicited events (money inserted, etc)"""
    events = []
    while not vmc.async_events.empty():
        events.append(vmc.async_events.get())
    return jsonify(events)

# --- STARTUP LOGIC ---
if __name__ == '__main__':
    # Start the Serial Driver before the web server
    try:
        print(f"[App] Starting VMC Driver on {SERIAL_PORT}...")
        vmc.start()
    except Exception as e:
        print(f"[App] Failed to start VMC Driver: {e}")

    # Run the Flask App
    app.run(host='0.0.0.0', port=5000, threaded=True)