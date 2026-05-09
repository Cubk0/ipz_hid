import pytest
from ipz_hid.core.descriptor import HIDDescriptor
from ipz_hid.core.device import HIDDevice
from ipz_hid.core.field import HIDField
from ipz_hid.core.hid_types import HIDInput, HIDInputField, HIDUsage
from ipz_hid.core.hid_items import *
from ipz_hid.core.hid_usages import *
from ipz_hid.linux.mapper import HIDLinuxMapper
from evdev import ecodes

mouse_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x02,        # Usage (Mouse)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x01,        # Usage (Pointer)
    0xA1, 0x00,        # Collection (Physical)
    0x05, 0x09,        # Usage Page (Button)
    0x19, 0x01,        # Usage Minimum (Button 1)
    0x29, 0x03,        # Usage Maximum (Button 3)
    0x15, 0x00,        # Logical Minimum (0)
    0x25, 0x01,        # Logical Maximum (1)
    0x95, 0x03,        # Report Count (3)
    0x75, 0x01,        # Report Size (1)
    0x81, 0x02,        # Input (Data, Variable, Absolute)
    0x95, 0x01,        # Report Count (1)
    0x75, 0x05,        # Report Size (5)
    0x81, 0x03,        # Input (Constant, Variable, Absolute)
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x30,        # Usage (X)
    0x09, 0x31,        # Usage (Y)
    0x09, 0x38,        # Usage (Wheel)
    0x15, 0x81,        # Logical Minimum (-127)
    0x25, 0x7F,        # Logical Maximum (127)
    0x75, 0x08,        # Report Size (8)
    0x95, 0x03,        # Report Count (3)
    0x81, 0x06,        # Input (Data, Variable, Relative)
    0xC0,              # End Collection
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
slider_dial_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x08,        # Usage (Multi-axis Controller) - VALID
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x36,        # Usage (Slider)
    0x09, 0x37,        # Usage (Dial)
    0x15, 0x00,        # Logical Minimum (0)
    0x25, 0xFF,        # Logical Maximum (255)
    0x75, 0x08,        # Report Size (8)
    0x95, 0x02,        # Report Count (2)
    0x81, 0x02,        # Input (Data, Variable, Absolute)
    0xC0               # End Collection
])

@pytest.fixture
def create_device_from_descriptor():
    def _create(descriptor_bytes):
        device = HIDDevice()
        device.set_descriptor(HIDDescriptor.from_bytes(descriptor_bytes))
        return device
    return _create

def test_mouse_axes(create_device_from_descriptor):
    device = create_device_from_descriptor(mouse_descriptor)
    print(device.fields[2].attributes)
    mapper = HIDLinuxMapper()
    abs_info_list = mapper.get_abs_axis_info(device.fields)
    rel_axes = mapper.get_supported_rel(device.fields)[0]
    abs_axes_found = set()
    for collection_dict in abs_info_list:
        abs_axes_found.update(collection_dict.keys())

    assert ecodes.ABS_X not in abs_axes_found
    assert ecodes.ABS_Y not in abs_axes_found
    assert ecodes.ABS_WHEEL not in abs_axes_found

    assert ecodes.REL_X in rel_axes
    assert ecodes.REL_Y in rel_axes
    assert ecodes.REL_WHEEL in rel_axes


def test_hat_switch_mapping(create_device_from_descriptor):
    device = create_device_from_descriptor(hat_switch_descriptor)
    mapper = HIDLinuxMapper()
    abs_info_list = mapper.get_abs_axis_info(device.fields)
    axes_found = set()
    for collection_dict in abs_info_list:
        axes_found.update(collection_dict.keys())
    assert ecodes.ABS_HAT0X in axes_found
    assert ecodes.ABS_HAT0Y in axes_found

def test_slider_and_dial(create_device_from_descriptor):
    device = create_device_from_descriptor(slider_dial_descriptor)
    mapper = HIDLinuxMapper()
    abs_info_list = mapper.get_abs_axis_info(device.fields)

    axes_found = set()
    for collection_dict in abs_info_list:
        axes_found.update(collection_dict.keys())

    assert ecodes.ABS_THROTTLE in axes_found
    assert ecodes.ABS_RUDDER in axes_found

def test_constant_fields_ignored(create_device_from_descriptor):
    descriptor_bytes = bytes([
        0x05, 0x01, 0x09, 0x02, 0xA1, 0x01,
        0x09, 0x30, 0x15, 0x00, 0x25, 0xFF,
        0x75, 0x08, 0x95, 0x01, 0x81, 0x03,  # Constant
        0xC0
    ])
    device = create_device_from_descriptor(descriptor_bytes)
    mapper = HIDLinuxMapper()
    abs_info_list = mapper.get_abs_axis_info(device.fields)

    for collection_dict in abs_info_list:
        assert collection_dict == {}
