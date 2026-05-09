from enum import IntEnum

class UsagePage(IntEnum):

    NONE = -1
    UNDEFINED = 0x00
    GENERIC_DESKTOP = 0x01
    SIMULATION_CONTROLS = 0x02
    VR_CONTROLS = 0x03
    SPORT_CONTROLS = 0x04
    GAME_CONTROLS = 0x05
    GENERIC_DEVICE_CONTROLS = 0x06
    KEYBOARD_KEYPAD = 0x07
    LEDS = 0x08
    BUTTON = 0x09
    ORDINAL = 0x0A
    TELEPHONY = 0x0B
    CONSUMER = 0x0C
    DIGITIZER = 0x0D
    HAPTICS = 0x0E
    PID = 0x0F  # Physical Interface Device
    UNICODE = 0x10
    ALPHANUMERIC_DISPLAY = 0x14
    MEDICAL_INSTRUMENT = 0x40
    MONITOR = 0x80
    MONITOR_ENUMERATED = 0x81
    VESA_VIRTUAL_CONTROLS = 0x82
    POWER_DEVICE = 0x84
    BATTERY_SYSTEM = 0x85
    BAR_CODE_SCANNER = 0x8C
    SCALE = 0x8D
    MSR = 0x8E  # Magnetic Stripe Reader
    CAMERA_CONTROL = 0x90
    ARCADE = 0x91

class GenericDesktopUsage(IntEnum):
    POINTER = 0x01
    MOUSE = 0x02
    JOYSTICK = 0x04
    GAME_PAD = 0x05
    KEYBOARD = 0x06
    KEYPAD = 0x07
    MULTI_AXIS_CONTROLLER = 0x08
    # System Control
    X = 0x30
    Y = 0x31
    Z = 0x32
    RX = 0x33
    RY = 0x34
    RZ = 0x35
    SLIDER = 0x36
    DIAL = 0x37
    WHEEL = 0x38
    HAT_SWITCH = 0x39
    COUNTED_BUFFER = 0x3A
    BYTE_COUNT = 0x3B
    MOTION_WAKEUP = 0x3C
    START = 0x3D
    SELECT = 0x3E
    Vx = 0x40
    Vy = 0x41
    Vz = 0x42
    Vbrx = 0x43
    Vbry = 0x44
    Vbrz = 0x45
    Vno = 0x46
    SYSTEM_CONTROL = 0x80
    SYSTEM_POWER_DOWN = 0x81
    SYSTEM_SLEEP = 0x82
    SYSTEM_WAKE_UP = 0x83
    SYSTEM_CONTEXT_MENU = 0x84
    SYSTEM_MAIN_MENU = 0x85
    SYSTEM_APP_MENU = 0x86
    SYSTEM_MENU_HELP = 0x87
    SYSTEM_MENU_EXIT = 0x88
    SYSTEM_MENU_SELECT = 0x89
    SYSTEM_MENU_RIGHT = 0x8A
    SYSTEM_MENU_LEFT = 0x8B
    SYSTEM_MENU_UP = 0x8C
    SYSTEM_MENU_DOWN = 0x8D

class KeyboardUsage(IntEnum):
    RESERVED = 0x00
    ERROR_ROLL_OVER = 0x01
    POST_FAIL = 0x02
    ERROR_UNDEFINED = 0x03
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0A
    H = 0x0B
    I = 0x0C
    J = 0x0D
    K = 0x0E
    L = 0x0F
    M = 0x10
    N = 0x11
    O = 0x12
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1A
    X = 0x1B
    Y = 0x1C
    Z = 0x1D
    
    # Numbers
    NUMBER_1 = 0x1E
    NUMBER_2 = 0x1F
    NUMBER_3 = 0x20
    NUMBER_4 = 0x21
    NUMBER_5 = 0x22
    NUMBER_6 = 0x23
    NUMBER_7 = 0x24
    NUMBER_8 = 0x25
    NUMBER_9 = 0x26
    NUMBER_0 = 0x27
    
    # Enter, escape, backspace, tab, space
    ENTER = 0x28
    ESCAPE = 0x29
    BACKSPACE = 0x2A
    TAB = 0x2B
    SPACEBAR = 0x2C
    
    # Symbols
    MINUS = 0x2D
    EQUAL = 0x2E
    LEFT_BRACKET = 0x2F
    RIGHT_BRACKET = 0x30
    BACKSLASH = 0x31
    NON_US_HASH = 0x32
    SEMICOLON = 0x33
    APOSTROPHE = 0x34
    GRAVE = 0x35
    COMMA = 0x36
    PERIOD = 0x37
    SLASH = 0x38
    CAPS_LOCK = 0x39
    
    # Function keys
    F1 = 0x3A
    F2 = 0x3B
    F3 = 0x3C
    F4 = 0x3D
    F5 = 0x3E
    F6 = 0x3F
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45
    
    # Control keys
    PRINT_SCREEN = 0x46
    SCROLL_LOCK = 0x47
    PAUSE = 0x48
    INSERT = 0x49
    HOME = 0x4A
    PAGE_UP = 0x4B
    DELETE = 0x4C
    END = 0x4D
    PAGE_DOWN = 0x4E
    RIGHT_ARROW = 0x4F
    LEFT_ARROW = 0x50
    DOWN_ARROW = 0x51
    UP_ARROW = 0x52
    
    # Keypad
    KEYPAD_NUM_LOCK = 0x53
    KEYPAD_DIVIDE = 0x54
    KEYPAD_MULTIPLY = 0x55
    KEYPAD_MINUS = 0x56
    KEYPAD_PLUS = 0x57
    KEYPAD_ENTER = 0x58
    KEYPAD_1 = 0x59
    KEYPAD_2 = 0x5A
    KEYPAD_3 = 0x5B
    KEYPAD_4 = 0x5C
    KEYPAD_5 = 0x5D
    KEYPAD_6 = 0x5E
    KEYPAD_7 = 0x5F
    KEYPAD_8 = 0x60
    KEYPAD_9 = 0x61
    KEYPAD_0 = 0x62
    KEYPAD_DOT = 0x63
    
    # Modifier keys left/right
    LEFT_CTRL = 0xE0
    LEFT_SHIFT = 0xE1
    LEFT_ALT = 0xE2
    LEFT_GUI = 0xE3
    RIGHT_CTRL = 0xE4
    RIGHT_SHIFT = 0xE5
    RIGHT_ALT = 0xE6
    RIGHT_GUI = 0xE7


class ButtonUsage(IntEnum):
    BUTTON_1  = 0x01
    BUTTON_2  = 0x02
    BUTTON_3  = 0x03
    BUTTON_4  = 0x04
    BUTTON_5  = 0x05
    BUTTON_6  = 0x06
    BUTTON_7  = 0x07
    BUTTON_8  = 0x08
    BUTTON_9  = 0x09
    BUTTON_10 = 0x0A
    BUTTON_11 = 0x0B
    BUTTON_12 = 0x0C
    BUTTON_13 = 0x0D
    BUTTON_14 = 0x0E
    BUTTON_15 = 0x0F
    BUTTON_16 = 0x10
    BUTTON_17 = 0x11
    BUTTON_18 = 0x12
    BUTTON_19 = 0x13
    BUTTON_20 = 0x14
    BUTTON_21 = 0x15
    BUTTON_22 = 0x16
    BUTTON_23 = 0x17
    BUTTON_24 = 0x18
    BUTTON_25 = 0x19
    BUTTON_26 = 0x1A
    BUTTON_27 = 0x1B
    BUTTON_28 = 0x1C
    BUTTON_29 = 0x1D
    BUTTON_30 = 0x1E
    BUTTON_31 = 0x1F
    BUTTON_32 = 0x20

class SimulationUsage(IntEnum):
    # Flight Simulation Devices
    FLIGHT_SIMULATION_DEVICE = 0x01
    AUTOMOBILE_SIMULATION_DEVICE = 0x02
    TANK_SIMULATION_DEVICE = 0x03
    SPACESHIP_SIMULATION_DEVICE = 0x04
    SUBMARINE_SIMULATION_DEVICE = 0x05
    SAILING_SIMULATION_DEVICE = 0x06
    MOTORCYCLE_SIMULATION_DEVICE = 0x07
    SPORTS_SIMULATION_DEVICE = 0x08
    AIRPLANE_SIMULATION_DEVICE = 0x09
    HELICOPTER_SIMULATION_DEVICE = 0x0A
    MAGIC_CARPET_SIMULATION_DEVICE = 0x0B
    BICYCLE_SIMULATION_DEVICE = 0x0C

    # Flight Control
    FLIGHT_CONTROL_STICK = 0x20
    FLIGHT_STICK = 0x21
    CYCLIC_CONTROL = 0x22
    CYCLIC_TRIM = 0x23
    FLIGHT_YOKE = 0x24
    TRACK_CONTROL = 0x25

    # Automotive Control
    AILERON = 0xB0
    AILERON_TRIM = 0xB1
    ANTI_TORQUE_CONTROL = 0xB2
    AUTOPILOT_ENABLE = 0xB3
    CHAFFER_RELEASE = 0xB4
    COLLECTIVE_CONTROL = 0xB5
    DIVE_BRAKE = 0xB6
    ELECTRONIC_COUNTERMEASURES = 0xB7
    ELEVATOR = 0xB8
    ELEVATOR_TRIM = 0xB9
    RUDDER = 0xBA
    THROTTLE = 0xBB
    FLIGHT_COMMUNICATIONS = 0xBC
    FLARE_RELEASE = 0xBD
    LANDING_GEAR = 0xBE
    TOE_BRAKE = 0xBF
    TRIGGER = 0xC0
    WEAPONS_ARM = 0xC1
    WEAPONS_SELECT = 0xC2
    WING_FLAPS = 0xC3
    ACCELERATOR = 0xC4
    BRAKE = 0xC5
    CLUTCH = 0xC6
    SHIFTER = 0xC7
    STEERING = 0xC8
    TURRET_DIRECTION = 0xC9
    BARREL_ELEVATION = 0xCA
    DIVE_PLANE = 0xCB
    BALLAST = 0xCC
    BICYCLE_CRANK = 0xCD
    HANDLE_BARS = 0xCE
    FRONT_BRAKE = 0xCF
    REAR_BRAKE = 0xD0
