from ipz_hid.core.hid_usages import *

def get_int_from_bytes(data: bytes, bit_offset: int, bit_size: int) -> int:
    full_int = int.from_bytes(data, 'little')
    mask = (1 << bit_size) - 1
    value = (full_int >> bit_offset) & mask
    return value

#def get_usage(page:UsagePage,usage_id:int):
#    match page:
#        case UsagePage.GENERIC_DESKTOP:
#            return GenericDesktopUsage(usage_id)
#        case UsagePage.KEYBOARD_KEYPAD:
#            return KeyboardUsage(usage_id)
#        case UsagePage.BUTTON:
#            return ButtonUsage(usage_id)
#        case _:
#            raise ValueError(f"Unsupported usage page {page}")

#def get_usage_page(usage:IntEnum):
#    match usage:
#        case GenericDesktopUsage():
#            return UsagePage.GENERIC_DESKTOP
#        case KeyboardUsage():
#            return UsagePage.KEYBOARD_KEYPAD
#        case ButtonUsage():
#            return UsagePage.BUTTON
#        case _:
#            raise ValueError(f"Unsupported usage {usage}")