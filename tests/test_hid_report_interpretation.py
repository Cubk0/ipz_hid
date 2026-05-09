from ipz_hid.core.descriptor import HIDDescriptor
from ipz_hid.core.device import HIDDevice
from ipz_hid.core.field import HIDField
from ipz_hid.core.hid_types import HIDInput, HIDInputField, HIDUsage
from ipz_hid.core.hid_items import *
from ipz_hid.core.hid_usages import *


report_id_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x02,        # Usage (Mouse)
    0xA1, 0x01,        # Collection (Application)
    0x85, 0x01,        #   Report ID (1)
    0x05, 0x09,        #   Usage Page (Button)
    0x19, 0x01,        #   Usage Minimum (Button 1)
    0x29, 0x02,        #   Usage Maximum (Button 2)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x02,        #   Report Count (2)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    0x75, 0x06,        #   Report Size (6)
    0x95, 0x01,        #   Report Count (1)
    0x81, 0x03,        #   Input (Constant)
    0x05, 0x01,        #   Usage Page (Generic Desktop)
    0x09, 0x30,        #   Usage (X)
    0x09, 0x31,        #   Usage (Y)
    0x15, 0x81,        #   Logical Minimum (-127)
    0x25, 0x7F,        #   Logical Maximum (127)
    0x75, 0x08,        #   Report Size (8)
    0x95, 0x02,        #   Report Count (2)
    0x81, 0x06,        #   Input (Data, Variable, Relative)
    0xC0,              # End Collection

    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x06,        # Usage (Keyboard)
    0xA1, 0x01,        # Collection (Application)
    0x85, 0x02,        #   Report ID (2)
    0x05, 0x07,        #   Usage Page (Key Codes)
    0x19, 0xE0,        #   Usage Minimum (224)
    0x29, 0xE7,        #   Usage Maximum (231)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x01,        #   Logical Maximum (1)
    0x75, 0x01,        #   Report Size (1)
    0x95, 0x08,        #   Report Count (8)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    0x75, 0x08,        #   Report Size (8)
    0x95, 0x01,        #   Report Count (1)
    0x81, 0x03,        #   Input (Constant)
    0x75, 0x08,        #   Report Size (8)
    0x95, 0x06,        #   Report Count (6)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x65,        #   Logical Maximum (101)
    0x05, 0x07,        #   Usage Page (Key Codes)
    0x19, 0x00,        #   Usage Minimum (0)
    0x29, 0x65,        #   Usage Maximum (101)
    0x81, 0x00,        #   Input (Data, Array)
    0xC0               # End Collection
])


def create_device(descriptor: bytes) -> HIDDevice:
    device:HIDDevice = HIDDevice()
    device.set_descriptor(HIDDescriptor.from_bytes(descriptor))
    return device


def test_mouse_report_is_parsed_using_report_id_parser():
    device = create_device(report_id_descriptor)

    report = bytes([0x01, 0b00000010, 0xFE, 0x03])  # ID 1, button 2, X=-2, Y=3
    parsed = device.parse_input_report(report)

    buttons:HIDInputField = parsed[0][0]
    axes:HIDInputField = parsed[0][1]

    assert buttons.input_array[0].usage == HIDUsage(UsagePage.BUTTON, ButtonUsage.BUTTON_1)
    assert buttons.input_array[0].value == 0
    assert buttons.input_array[1].usage == HIDUsage(UsagePage.BUTTON, ButtonUsage.BUTTON_2)
    assert buttons.input_array[1].value == 1
    assert axes.input_array[0].usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.X)
    assert axes.input_array[0].value == -2
    assert axes.input_array[1].usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.Y)
    assert axes.input_array[1].value == 3


def test_keyboard_report_is_grouped_by_top_level_collection():
    device = create_device(report_id_descriptor)

    report = bytes([0x02, 0x04, 0x00, 0x05, 0, 0, 0, 0, 0])  # ID 2, LEFT_ALT + B
    parsed = device.parse_input_report(report)

    assert parsed[0] == []
    modifier_keys:HIDInputField = parsed[1][0]
    array_keys:HIDInputField = parsed[1][1]

    assert modifier_keys.input_array[2].usage == HIDUsage(UsagePage.KEYBOARD_KEYPAD, KeyboardUsage.LEFT_ALT)
    assert modifier_keys.input_array[2].value == 1
    assert array_keys.input_array[0].usage == HIDUsage(UsagePage.KEYBOARD_KEYPAD, KeyboardUsage.B)
