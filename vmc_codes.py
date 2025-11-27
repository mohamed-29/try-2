# vmc_codes.py
# Contains all Hex codes, Protocol Rules, and Response Mappings

# --- PROTOCOL CONSTANTS ---
STX = [0xFA, 0xFB]
CMD_POLL = 0x41
CMD_ACK = 0x42

# --- 1. COMMANDS SENT BY US (UPPER COMPUTER) ---
CMD_SEND = {
    # Payment
    "REQUEST_GIVE_CHANGE": 0x25,
    "NOTIFY_CASHLESS_PAYMENT": 0x27,
    "SET_PAYMENT_ACCEPTANCE": 0x28,

    # Selection & Config
    "SET_PRICE": 0x12,
    "SET_INVENTORY": 0x13,
    "SET_CAPACITY": 0x14,
    "SET_PRODUCT_ID": 0x15,

    # Dispensing
    "CHECK_SELECTION_STATUS": 0x01,
    "DISPENSE_ITEM": 0x03,
    "CANCEL_SELECTION": 0x05,
    "DIRECT_DRIVE_MOTOR": 0x06,

    # System
    "SET_POLL_INTERVAL": 0x16,
    "REQUEST_INFO_SYNC": 0x31,
    "REQUEST_STATUS_SIMPLE": 0x53,
    "REQUEST_STATUS_FULL": 0x51,
    "CHECK_IC_CARD_BALANCE": 0x61,
    "REQUEST_CARD_DEDUCTION": 0x64,
    
    # Menu Wrapper (All settings use this)
    "MENU_COMMAND_WRAPPER": 0x70
}

# --- 2. COMMANDS RECEIVED FROM VMC (RESPONSES) ---
CMD_RECV = {
    0x41: "POLL",
    0x42: "ACK",
    
    # Dispensing Responses
    0x02: "SELECTION_CHECK_RESULT", # Response to 0x01
    0x04: "DISPENSING_STATUS",      # Response to 0x03 (Buy)
    0x54: "MACHINE_STATUS_SIMPLE",  # Response to 0x53

    # Info Responses
    0x11: "SELECTION_INFO_REPORT",  # Response to 0x31 (Sync) or 0x11 query
    0x23: "CURRENT_AMOUNT_REPORT",
    0x21: "MONEY_RECEIVED_NOTICE",
    0x52: "MACHINE_STATUS_FULL",
    
    # Menu Response
    0x71: "MENU_SETTING_RESPONSE"
}

# --- 3. RESPONSE EXPECTATION MAP ---
# This dictionary tells the Driver: 
# "If I send Command X, block and wait until I receive Command Y."
# If a command is NOT in this list, the Driver will only wait for an ACK.
EXPECTED_RESPONSES = {
    0x01: 0x02,  # Check Status -> Expect Result
    0x03: 0x04,  # Dispense -> Expect Dispense Status
    0x53: 0x54,  # Status Req -> Expect Status Data
    0x51: 0x52,  # Full Status Req -> Expect Full Status Data
    0x31: 0x11,  # Sync Req -> Expect Selection Info
    0x70: 0x71,  # Menu Command -> Expect Menu Response
    0x61: 0x62,  # Check Card -> Expect Balance
}

# --- 4. ERROR CODES (For decoding response bytes) ---
DISPENSE_STATUS_CODES = {
    0x01: "Dispensing...",
    0x02: "Dispensing Success",
    0x03: "Selection Jammed",
    0x04: "Motor Error",
    0x07: "Elevator Error",
    0xFF: "Terminated"
}