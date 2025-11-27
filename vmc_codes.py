# vmc_codes.py
# Contains all Hex codes, Protocol Rules, and Response Mappings
# Dictionary mapping VMC Hex Command Bytes to Readable Names
# These are commands received FROM the VMC (VMC -> Upper Computer)

VMC_INCOMING_COMMANDS = {
    # --- Protocol Basics ---
    0x41: "POLL",                      # VMC asking: "Do you have instructions?"
    0x42: "ACK",                       # VMC acknowledging our last message
    
    # --- Payment & Money (Section 4.1) ---
    0x21: "MONEY_RECEIVED_NOTICE",     # VMC received cash/coin (4.1.1)
    0x23: "CURRENT_AMOUNT_REPORT",     # VMC reports total credit available (4.1.2)
    0x24: "POS_DISPLAY_REQUEST",       # VMC asks to show info on screen (4.1.3)
    0x26: "CHANGE_GIVEN_RESULT",       # Result of 'Give Change' request (4.1.4 response)
    
    # --- Selection & Tray Info (Section 4.2) ---
    0x11: "SELECTION_INFO_REPORT",     # Price, Inventory, Capacity, ID (4.2.1)
    0x17: "ONE_KEY_FULL_LOADING",      # User pressed "Fill All" button on machine (4.2.6)
    
    # --- Dispensing & Operation (Section 4.3) ---
    0x02: "SELECTION_CHECK_RESULT",    # Result of "Check Selection" (0x01 response)
    0x04: "DISPENSING_STATUS",         # Critical: Success, Jammed, Motor Error (4.3.3)
    0x05: "SELECTION_MADE_CANCEL",     # User selected item via keypad (4.3.4)
    0x54: "MACHINE_STATUS_SIMPLE",     # Simple status: Door open, Elevator error (Response to 0x53)
    
    # --- System & Misc (Section 4.4) ---
    0x62: "IC_CARD_BALANCE",           # Balance info (Response to 0x61)
    0x63: "CALL_ANDROID_MENU",         # Request to open settings menu (4.4.2)
    0x31: "INFO_SYNC_REQUEST",         # Startup synchronization (4.4.4)
    0x52: "MACHINE_STATUS_FULL",       # Detailed status: Temp, humidity, peripherals (Response to 0x51)
    0x66: "MICROWAVE_INFO",            # Microwave status report (4.1.7)
    
    # --- Menu Settings Responses (Section 4.5) ---
    # The VMC sends 0x71 for almost all settings queries. 
    # We must look at the byte *inside* the payload to know which setting it is.
    0x71: "MENU_SETTING_RESPONSE"      # Wrapper for all settings (Coin system, Temp, etc.)
}

# Sub-dictionary for 0x71 payloads
# If command is 0x71, look at data[0] (Command Type) to identify the specific setting
MENU_COMMAND_TYPES = {
    0x01: "COIN_SYSTEM_SETTING",
    0x02: "SELECTION_MODE_SETTING",
    0x03: "MOTOR_AD_SETTING",
    0x04: "SELECTION_COUPLING",
    0x05: "CLEAR_COUPLING",
    0x06: "COUPLING_SYNC_TIME",
    0x07: "MOTOR_SHORT_VALUE",
    0x08: "MACHINE_ID",
    0x09: "SYSTEM_TIME",
    0x10: "DECIMAL_POINT",
    0x11: "DELIVERY_DOOR_CLOSE_TIME",
    0x12: "CONNECTING_LIFT",
    0x13: "ANTI_THEFT_BOARD_TIME",
    0x14: "50C_COIN_COUNT",            # Chinese market
    0x15: "1_DOLLAR_COIN_COUNT",       # Chinese market
    0x16: "LIGHT_CONTROL",
    0x17: "UNIONPAY_POS_SETTING",
    0x18: "BILL_VALUE_ACCEPTED",
    0x19: "BILL_ACCEPTING_MODE",
    0x20: "BILL_LOW_CHANGE",
    0x21: "AUTO_CHANGE_TIME",
    0x22: "AUTO_HOLDING_TIME",
    0x23: "REMAINING_CREDIT_MODE",
    0x24: "DROP_SENSOR_SETTING",
    0x25: "BELT_DETECTION_SETTING",
    0x26: "EXTRA_QUARTER_TURN",
    0x27: "JAMMED_SELECTION_ACTION",
    0x28: "TEMP_CONTROLLER_SETTING",
    0x29: "COMPRESSOR_PERIOD",
    0x30: "CLEAR_SALES_INFO",
    0x31: "CLEAR_SECURITY_CODE",
    0x32: "CLEAR_JAMMED_SELECTION",
    0x33: "CLEAR_MOTOR_ERROR",
    0x34: "CLEAR_LIFT_ERROR",
    0x35: "CLEAR_QUARTER_TURN_ERROR",
    0x36: "QUERY_TEMP_CONTROLLER",
    0x37: "TEMP_CONTROLLER_PARAMS",
    0x38: "SELECTION_TEST",
    0x39: "COIN_OUT_TESTING",
    0x40: "QUERY_COIN_NUMBER",
    0x41: "QUERY_SELECTION_NUMBER",
    0x42: "QUERY_SELECTION_CONFIG",
    0x43: "DAILY_SALES",
    0x44: "MONTHLY_SALES",
    0x45: "YEARLY_SALES",
    0x46: "ENTIRE_MACHINE_SALES",
    0x47: "SELECTION_SALES_MSG",
    0x48: "DROP_SENSOR_FREQ_ADJ",
    0x49: "DROP_SENSOR_SENSITIVITY",
    0x50: "DROP_SENSOR_TEST",
    0x51: "LIFT_LAYER_LOCATION",
    0x52: "LIFT_SPEED",
    0x53: "LIFT_SENSITIVITY",
    0x54: "LIFT_TEST",
    0x55: "MICROWAVE_LOCATION",
    0x56: "SPACE_BETWEEN_BOXES",
    0x57: "MECHANISM_TEST_LUNCHBOX",
    0x58: "LUNCH_BOX_MACHINE_TEST",
    0x59: "BILL_CHANGE",
    0x60: "CONNECT_TEMP_CONTROLLER",
    0x61: "BILL_ACCEPTOR_DIAG",
    0x62: "COIN_ACCEPTOR_DIAG",
    0x63: "FULLY_LOADING",
    0x64: "LUNCH_BOX_HEATING_TIME",
    0x65: "HEAT_LUNCH_BOX_SETTING",
    0x67: "LOCATE_LUNCH_BOX_MANUAL",
    0x68: "LUNCH_BOX_SPEED",
    0x69: "LUNCH_BOX_SENSITIVITY",
    0x70: "SYSTEM_DATA_EXPORT",
    0x71: "SYSTEM_DATA_IMPORT",
    0x72: "TEST_DROP_SENSOR_LUNCHBOX",
    0x78: "SENSOR_STATUS_LUNCHBOX"
}

UPPER_COMPUTER_COMMANDS = {
    # --- Protocol ---
    "ACK": 0x42,                           # Acknowledge receiving data from VMC
    
    # --- Payment (Section 4.1) ---
    "REQUEST_GIVE_CHANGE": 0x25,           # Ask VMC to payout change (4.1.4)
    "NOTIFY_CASHLESS_PAYMENT": 0x27,       # Tell VMC we received money via App/QR (4.1.5)
    "SET_PAYMENT_ACCEPTANCE": 0x28,        # Enable/Disable Coins or Notes (4.1.6)
    
    # --- Selection Configuration (Section 4.2) ---
    "SET_PRICE": 0x12,                     # Set price for slot(s) (4.2.2)
    "SET_INVENTORY": 0x13,                 # Set stock count (4.2.3)
    "SET_CAPACITY": 0x14,                  # Set max capacity (4.2.4)
    "SET_PRODUCT_ID": 0x15,                # Set product ID code (4.2.5)
    
    # --- Dispensing & Control (Section 4.3) ---
    "CHECK_SELECTION_STATUS": 0x01,        # Pre-check if motor/slot is okay (4.3.1)
    "DISPENSE_ITEM": 0x03,                 # The main "Buy" command (4.3.2)
    "CANCEL_SELECTION": 0x05,              # Deselect/Cancel (4.3.4)
    "DIRECT_DRIVE_MOTOR": 0x06,            # Engineering: Force motor spin (4.3.5)
    
    # --- System & Status (Section 4.4) ---
    "SET_POLL_INTERVAL": 0x16,             # Adjust how often VMC polls us (4.4.3)
    "REQUEST_INFO_SYNC": 0x31,             # Ask VMC to send all prices/stock (4.4.4)
    "REQUEST_STATUS_SIMPLE": 0x53,         # Basic errors (Door, Elevator) (Page 13)
    "REQUEST_STATUS_FULL": 0x51,           # Full sensors (Temp, Peripherals) (Page 15)
    "CHECK_IC_CARD_BALANCE": 0x61,         # Query card reader balance (4.4.1)
    "REQUEST_CARD_DEDUCTION": 0x64,        # Ask VMC to deduct from card (4.4.6)
    
    # --- Menu / Settings Wrapper (Section 4.5) ---
    # This is the command used for ALL settings below.
    # The specific setting is defined by the first byte of the data payload.
    "MENU_COMMAND_WRAPPER": 0x70
}

# --- 2. Menu Sub-Commands (For 0x70) ---
# When sending 0x70, the first byte of your data payload must be one of these:
MENU_SUB_COMMANDS = {
    # Payment Config
    "COIN_SYSTEM_SETTING": 0x01,
    "UNIONPAY_POS_SETTING": 0x17,
    "BILL_VALUE_ACCEPTED": 0x18,
    "BILL_ACCEPTING_MODE": 0x19,
    "BILL_LOW_CHANGE": 0x20,
    "AUTO_CHANGE_TIME": 0x21,
    "AUTO_HOLDING_TIME": 0x22,
    "REMAINING_CREDIT_MODE": 0x23,
    "BILL_CHANGE_TEST": 0x59,
    "BILL_ACCEPTOR_DIAG": 0x61,
    "COIN_ACCEPTOR_DIAG": 0x62,
    
    # Machine Config
    "MACHINE_ID": 0x08,
    "SYSTEM_TIME": 0x09,
    "DECIMAL_POINT": 0x10,
    "LIGHT_CONTROL": 0x16,
    "CLEAR_SALES_INFO": 0x30,
    "CLEAR_SECURITY_CODE": 0x31,
    "FACTORY_RESET_LOADING": 0x63,         # "Fully Loading"
    "SYSTEM_DATA_EXPORT": 0x70,
    "SYSTEM_DATA_IMPORT": 0x71,

    # Hardware / Motor Config
    "SELECTION_MODE_SETTING": 0x02,        # Belt vs Spiral
    "MOTOR_AD_SETTING": 0x03,
    "SELECTION_COUPLING": 0x04,
    "CLEAR_COUPLING": 0x05,
    "COUPLING_SYNC_TIME": 0x06,
    "MOTOR_SHORT_VALUE": 0x07,
    "DELIVERY_DOOR_CLOSE_TIME": 0x11,
    "CONNECTING_LIFT": 0x12,
    "ANTI_THEFT_BOARD_TIME": 0x13,
    "DROP_SENSOR_SETTING": 0x24,
    "BELT_DETECTION_SETTING": 0x25,
    "EXTRA_QUARTER_TURN": 0x26,
    "JAMMED_SELECTION_ACTION": 0x27,       # Stop vs Continue
    "DROP_SENSOR_FREQ_ADJ": 0x48,
    "DROP_SENSOR_SENSITIVITY": 0x49,
    
    # Temperature / Refrigeration
    "TEMP_CONTROLLER_SETTING": 0x28,       # Mode: Heating/Cooling
    "COMPRESSOR_PERIOD": 0x29,
    "QUERY_TEMP_CONTROLLER": 0x36,
    "TEMP_CONTROLLER_PARAMS": 0x37,
    "CONNECT_TEMP_CONTROLLER": 0x60,
    
    # Errors & Maintenance
    "CLEAR_JAMMED_SELECTION": 0x32,
    "CLEAR_MOTOR_ERROR": 0x33,
    "CLEAR_LIFT_ERROR": 0x34,
    "CLEAR_QUARTER_TURN_ERROR": 0x35,
    
    # Tests
    "SELECTION_TEST": 0x38,
    "COIN_OUT_TESTING": 0x39,
    "DROP_SENSOR_TEST": 0x50,
    "LIFT_TEST": 0x54,
    
    # Sales Data Queries
    "QUERY_COIN_NUMBER": 0x40,
    "QUERY_SELECTION_NUMBER": 0x41,
    "QUERY_SELECTION_CONFIG": 0x42,        # Config of a specific slot
    "DAILY_SALES": 0x43,
    "MONTHLY_SALES": 0x44,
    "YEARLY_SALES": 0x45,
    "ENTIRE_MACHINE_SALES": 0x46,
    "SELECTION_SALES_MSG": 0x47,
    
    # Lift & Lunchbox Specifics
    "LIFT_LAYER_LOCATION": 0x51,
    "LIFT_SPEED": 0x52,
    "LIFT_SENSITIVITY": 0x53,
    "MICROWAVE_LOCATION": 0x55,
    "SPACE_BETWEEN_BOXES": 0x56,
    "MECHANISM_TEST_LUNCHBOX": 0x57,
    "LUNCH_BOX_MACHINE_TEST": 0x58,
    "LUNCH_BOX_HEATING_TIME": 0x64,
    "HEAT_LUNCH_BOX_SETTING": 0x65,
    "LOCATE_LUNCH_BOX_MANUAL": 0x67,
    "LUNCH_BOX_SPEED": 0x68,
    "LUNCH_BOX_SENSITIVITY": 0x69,
    "TEST_DROP_SENSOR_LUNCHBOX": 0x72,
    "SENSOR_STATUS_LUNCHBOX": 0x78
}

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