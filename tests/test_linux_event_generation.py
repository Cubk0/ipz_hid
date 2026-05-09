from ipz_hid.core.descriptor import HIDDescriptor
from ipz_hid.core.device import HIDDevice
from ipz_hid.core.field import HIDField
from ipz_hid.core.hid_types import HIDInput, HIDInputField, HIDUsage
from ipz_hid.core.hid_items import *
from ipz_hid.core.hid_usages import *
from ipz_hid.linux.input_state import *
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

hat_switch_descriptor = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x05,        # Usage (Game Pad)
    0xA1, 0x01,        # Collection (Application)
    0x09, 0x39,        #   Usage (Hat Switch)
    0x15, 0x00,        #   Logical Minimum (0)
    0x25, 0x07,        #   Logical Maximum (7)
    0x75, 0x04,        #   Report Size (4)
    0x95, 0x01,        #   Report Count (1)
    0x81, 0x02,        #   Input (Data, Variable, Absolute)
    0xC0               # End Collection
])


def create_device(descriptor: bytes) -> HIDDevice:
    device:HIDDevice = HIDDevice()
    device.set_descriptor(HIDDescriptor.from_bytes(descriptor))
    return device


def create_event_generator(device: HIDDevice) -> EventGenerator:
    mapper = HIDLinuxMapper()
    return EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=mapper.get_supported_rel(device.fields)[0],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )


def test_mouse_relative_axes_generate_events_from_current_delta():
    device = create_device(mouse_descriptor)
    mapper = HIDLinuxMapper()
    gen = create_event_generator(device)

    report = bytes([0x00, 0x05, 0xFD, 0x01])  # X=5, Y=-3, Wheel=1
    parsed = device.parse_input_report(report)
    state = mapper.map(parsed[0])
    events = gen.diff(InputState(), state)

    rel_events = {
        (e.code, e.value)
        for e in events
        if e.type == ecodes.EV_REL
    }
    assert (ecodes.REL_X, 5) in rel_events
    assert (ecodes.REL_Y, -3) in rel_events
    assert (ecodes.REL_WHEEL, 1) in rel_events
    assert events[-1].type == ecodes.EV_SYN


def test_mouse_button_release_generates_key_release_event():
    device = create_device(mouse_descriptor)
    mapper = HIDLinuxMapper()
    gen = create_event_generator(device)

    pressed_report = bytes([0b00000001, 0, 0, 0])
    released_report = bytes([0, 0, 0, 0])

    pressed_state = mapper.map(device.parse_input_report(pressed_report)[0])
    released_state = mapper.map(device.parse_input_report(released_report)[0])

    events = gen.diff(pressed_state, released_state)

    assert any(e.type == ecodes.EV_KEY and e.code == ecodes.BTN_LEFT and e.value == 0 for e in events)
    assert events[-1].type == ecodes.EV_SYN


def test_absolute_axes_generate_abs_events_from_changed_state():
    device = create_device(absolute_xy_descriptor)
    mapper = HIDLinuxMapper()
    gen = create_event_generator(device)

    parsed = device.parse_input_report(bytes([10, 90]))
    state = mapper.map(parsed[0])
    events = gen.diff(InputState(), state)

    abs_events = {
        (e.code, e.value)
        for e in events
        if e.type == ecodes.EV_ABS
    }
    assert (ecodes.ABS_X, 10) in abs_events
    assert (ecodes.ABS_Y, 90) in abs_events
    assert events[-1].type == ecodes.EV_SYN


def test_hat_switch_report_generates_two_absolute_axis_events():
    device = create_device(hat_switch_descriptor)
    mapper = HIDLinuxMapper()
    gen = create_event_generator(device)

    parsed = device.parse_input_report(bytes([0x01]))  # Up-right
    state = mapper.map(parsed[0])
    events = gen.diff(InputState(), state)

    abs_events = {
        (e.code, e.value)
        for e in events
        if e.type == ecodes.EV_ABS
    }
    assert (ecodes.ABS_HAT0X, 1) in abs_events
    assert (ecodes.ABS_HAT0Y, -1) in abs_events
    assert events[-1].type == ecodes.EV_SYN
