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


def test_report_id_descriptor_creates_separate_input_parsers():
    device = create_device(report_id_descriptor)

    assert device.using_report_ids == True
    assert 1 in device.input_report_parsers
    assert 2 in device.input_report_parsers

    mouse_fields = device.input_report_parsers[1].fields
    keyboard_fields = device.input_report_parsers[2].fields

    assert len(mouse_fields) == 3
    assert len(keyboard_fields) == 3
    assert mouse_fields[0].report_id == 1
    assert keyboard_fields[0].report_id == 2
    assert mouse_fields[0].bit_offset == 0
    assert mouse_fields[1].bit_offset == 2
    assert mouse_fields[2].bit_offset == 8
