from ipz_hid.core.HID_classes import *
from ipz_hid.linux.mapper import HIDLinuxMapper
from evdev import ecodes


mouse_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x02,        # Usage (Mouse)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x01,        #   Usage (Pointer)
    0xA1, 0x00,        #   Collection (Physical)
    0x05, 0x09,        #     Usage Page (Button)
    0x19, 0x01,        #     Usage Minimum (Button 1)
    0x29, 0x03,        #     Usage Maximum (Button 3)
    0x15, 0x00,        #     Logical Minimum (0)
    0x25, 0x01,        #     Logical Maximum (1)
    0x95, 0x03,        #     Report Count (3)
    0x75, 0x01,        #     Report Size (1)
    0x81, 0x02,        #     Input (Data, Variable, Absolute)
    0x95, 0x01,        #     Report Count (1)
    0x75, 0x05,        #     Report Size (5)
    0x81, 0x03,        #     Input (Constant)
    0x05, 0x01,        #     Usage Page (Generic Desktop)
    0x09, 0x30,        #     Usage (X)
    0x09, 0x31,        #     Usage (Y)
    0x09, 0x38,        #     Usage (Wheel)
    0x15, 0x81,        #     Logical Minimum (-127)
    0x25, 0x7F,        #     Logical Maximum (127)
    0x75, 0x08,        #     Report Size (8)
    0x95, 0x03,        #     Report Count (3)
    0x81, 0x06,        #     Input (Data, Variable, Relative)
    0xC0,              #   End Collection
    0xC0               # End Collection
])

absolute_xy_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x04,        # Usage (Joystick)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x30,        #   Usage (X)
    0x09, 0x31,        #   Usage (Y)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x64,        #   Logical Maximum (100)
    0x75, 0x08,        #   Report Size (8)
    0x95, 0x02,        #   Report Count (2)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    0xC0               # End Collection
])

gamepad_button_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x05,        # Usage (Game Pad)
    0xA1, 0x01,        # Collection (Application)
    0x05, 0x09,        #   Usage Page (Button)
    0x19, 0x01,        #   Usage Minimum (Button 1)
    0x29, 0x02,        #   Usage Maximum (Button 2)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x02,        #   Report Count (2)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    0xC0               # End Collection
])

hat_switch_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x05,        # Usage (Game Pad)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x39,        # Usage (Hat Switch)
    0x15, 0x00,        # Logical Minimum (0)
    0x25, 0x07,        # Logical Maximum (7)
    0x75, 0x04,        # Report Size (4)
    0x95, 0x01,        # Report Count (1)
    0x81, 0x02,        # Input (Data, Variable, Absolute)
    0xC0               # End Collection
])


def create_device(descriptor: bytes) -> HIDDevice:
    device:HIDDevice = HIDDevice()
    device.set_descriptor(HIDDescriptor.from_bytes(descriptor))
    return device


def test_gamepad_buttons_are_mapped_to_generic_linux_button_codes():
    device = create_device(gamepad_button_descriptor)
    mapper = HIDLinuxMapper()

    supported_keys = mapper.get_supported_keys(device.fields)[0]

    assert ecodes.BTN_0 in supported_keys
    assert ecodes.BTN_1 in supported_keys
    assert ecodes.BTN_LEFT not in supported_keys
    assert ecodes.BTN_RIGHT not in supported_keys


def test_mouse_buttons_are_mapped_to_mouse_linux_button_codes():
    device = create_device(mouse_descriptor)
    mapper = HIDLinuxMapper()

    supported_keys = mapper.get_supported_keys(device.fields)[0]

    assert ecodes.BTN_LEFT in supported_keys
    assert ecodes.BTN_RIGHT in supported_keys
    assert ecodes.BTN_MIDDLE in supported_keys
    assert ecodes.BTN_0 not in supported_keys


def test_absolute_axes_are_mapped_to_linux_abs_codes_with_limits():
    device = create_device(absolute_xy_descriptor)
    mapper = HIDLinuxMapper()

    abs_info = mapper.get_abs_axis_info(device.fields)[0]

    assert ecodes.ABS_X in abs_info
    assert ecodes.ABS_Y in abs_info
    assert abs_info[ecodes.ABS_X].minimum == 0
    assert abs_info[ecodes.ABS_X].maximum == 100


def test_hat_switch_is_mapped_to_two_linux_abs_axes():
    device = create_device(hat_switch_descriptor)
    mapper = HIDLinuxMapper()

    abs_info = mapper.get_abs_axis_info(device.fields)[0]

    assert ecodes.ABS_HAT0X in abs_info
    assert ecodes.ABS_HAT0Y in abs_info
    assert abs_info[ecodes.ABS_HAT0X].minimum == -1
    assert abs_info[ecodes.ABS_HAT0X].maximum == 1
