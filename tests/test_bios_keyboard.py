from ipz_hid.core.HID_classes import *
from ipz_hid.core.HID_usages import *
from ipz_hid.linux.input_state import *
from ipz_hid.linux.mapper import HIDLinuxMapper
from ipz_hid.core.HID_items import *
from evdev import ecodes

descriptor = bytes([
        0x05, 0x01,        # Usage Page (Generic Desktop)
        0x09, 0x06,        # Usage (Keyboard)
        0xA1, 0x01,        # Collection (Application)
        0x05, 0x07,        #   Usage Page (Key Codes)
        0x19, 0xE0,        #   Usage Minimum (224)
        0x29, 0xE7,        #   Usage Maximum (231)
        0x15, 0x00,        #   Logical Minimum (0)
        0x25, 0x01,        #   Logical Maximum (1)
        0x75, 0x01,        #   Report Size (1)
        0x95, 0x08,        #   Report Count (8)
        0x81, 0x02,        #   Input (Data, Variable, Absolute) ; Modifier byte
        0x95, 0x01,        #   Report Count (1)
        0x75, 0x08,        #   Report Size (8)
        0x81, 0x03,        #   Input (Constant) ; Reserved byte
        0x95, 0x05,        #   Report Count (5)
        0x75, 0x01,        #   Report Size (1)
        0x05, 0x08,        #   Usage Page (LEDs)
        0x19, 0x01,        #   Usage Minimum (1)
        0x29, 0x05,        #   Usage Maximum (5)
        0x91, 0x02,        #   Output (Data, Variable, Absolute) ; LED report
        0x95, 0x01,        #   Report Count (1)
        0x75, 0x03,        #   Report Size (3)
        0x91, 0x03,        #   Output (Constant) ; LED report padding
        0x95, 0x06,        #   Report Count (6)
        0x75, 0x08,        #   Report Size (8)
        0x15, 0x00,        #   Logical Minimum (0)
        0x25, 0x65,        #   Logical Maximum (101)
        0x05, 0x07,        #   Usage Page (Key Codes)
        0x19, 0x00,        #   Usage Minimum (0)
        0x29, 0x65,        #   Usage Maximum (101)
        0x81, 0x00,        #   Input (Data, Array)
        0xC0               # End Collection
    ])

descriptor_from_items = [
    UsagePageItem(UsagePage.GENERIC_DESKTOP),
    UsageItem(GenericDesktopUsage.KEYBOARD),
    CollectionItem(HIDCollectionType.APPLICATION),
    UsagePageItem(UsagePage.KEYBOARD_KEYPAD),
    UsageMinimumItem(KeyboardUsage.LEFT_CTRL),
    UsageMaximumItem(KeyboardUsage.RIGHT_GUI),
    LogicalMinItem(0),
    LogicalMaxItem(1),
    ReportSizeItem(1),
    ReportCountItem(8),
    InputItem(HIDFieldAttributes(is_variable=True)),
    ReportCountItem(1),
    ReportSizeItem(8),
    InputItem(HIDFieldAttributes(is_constant=True)),
    ReportCountItem(6),
    ReportSizeItem(8),
    LogicalMinItem(0),
    LogicalMaxItem(101),
    UsagePageItem(UsagePage.KEYBOARD_KEYPAD),
    UsageMinimumItem(0),
    UsageMaximumItem(101),
    InputItem(HIDFieldAttributes(is_variable=False)),
    EndCollectionItem()
]
def parse_and_map(device: HIDDevice, mapper: HIDLinuxMapper, report: bytes) -> InputState:
    parsed = device.parse_input_report(report)
    return mapper.map(parsed[0])

def get_test_device() -> HIDDevice:
  device:HIDDevice= HIDDevice()
  device.set_descriptor(HIDDescriptor.from_bytes(descriptor));
  return device;

def test_parse_descriptor():
  device:HIDDevice= HIDDevice()
  device.set_descriptor(HIDDescriptor.from_bytes(descriptor));
  assert len(device.collections) == 1
  assert device.collections[0].usage == HIDUsage(UsagePage.GENERIC_DESKTOP,GenericDesktopUsage.KEYBOARD)
  assert len(device.fields) == 5
  modifier_field:HIDField = device.fields[0]
  assert modifier_field.attributes.is_variable == True;
  assert modifier_field.attributes.is_constant == False;
  assert modifier_field.report_size == 1
  assert modifier_field.report_count == 8
  assert modifier_field.logical_min == 0
  assert modifier_field.logical_max == 1
  assert modifier_field.application_collection!=None
  assert modifier_field.logical_collection==None
  assert modifier_field.physical_collection==None

  array_field:HIDField = device.fields[4]
  assert array_field.attributes.is_variable == False;
  assert array_field.attributes.is_constant == False;
  assert array_field.report_size == 8
  assert array_field.report_count == 6
  assert array_field.application_collection!=None
  assert array_field.logical_collection==None
  assert array_field.physical_collection==None
def test_parse_keys():
  device:HIDDevice = get_test_device()
  report = bytes([0x01, 0x00, 0x04, 0x39, 0x00, 0x00, 0x00, 0x00])
  parsed = device.parse_input_report(report);
  modifier_keys:HIDInputField = parsed[0][0]
  assert modifier_keys.field.application_collection != None
  assert modifier_keys.field.application_collection.usage == HIDUsage(UsagePage.GENERIC_DESKTOP,GenericDesktopUsage.KEYBOARD)
  assert modifier_keys.field.application_collection.type == HIDCollectionType.APPLICATION
  assert modifier_keys.input_array[0].usage == HIDUsage(UsagePage.KEYBOARD_KEYPAD,KeyboardUsage.LEFT_CTRL)
  array_keys:HIDInputField = parsed[0][1]
  assert array_keys.field.application_collection !=None
  assert array_keys.field.application_collection.usage == HIDUsage(UsagePage.GENERIC_DESKTOP,GenericDesktopUsage.KEYBOARD)
  assert array_keys.field.application_collection.type == HIDCollectionType.APPLICATION
  array:list[HIDInput] = array_keys.input_array
  assert array[0].usage == HIDUsage(UsagePage.KEYBOARD_KEYPAD,KeyboardUsage.A)
  assert array[1].usage == HIDUsage(UsagePage.KEYBOARD_KEYPAD,KeyboardUsage.CAPS_LOCK)

def test_linux_keyboard_event_generation():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )

    prev = InputState()

    report = bytes([0x01, 0x00, 0x04, 0x39, 0x00, 0x00, 0x00, 0x00])
    parsed = device.parse_input_report(report)

    curr = mapper.map(parsed[0])

    events = gen.diff(prev, curr)
    key_events = {
        (e.code, e.value)
        for e in events
        if e.type == ecodes.EV_KEY
    }
    assert (ecodes.KEY_LEFTCTRL, 1) in key_events
    assert (ecodes.KEY_A, 1) in key_events
    assert (ecodes.KEY_CAPSLOCK, 1) in key_events

    # Must end with SYN_REPORT
    assert events[-1].type == ecodes.EV_SYN

def test_linux_keyboard_modifier_only():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )

    prev = InputState()

    report = bytes([0x02, 0x00, 0, 0, 0, 0, 0, 0])  # LEFT_SHIFT
    parsed = device.parse_input_report(report)

    curr = mapper.map(parsed[0])
    events = gen.diff(prev, curr)

    assert any(
        e.type == ecodes.EV_KEY
        and e.code == ecodes.KEY_LEFTSHIFT
        and e.value == 1
        for e in events
    )
def test_linux_keyboard_multiple_modifiers():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )


    prev = InputState()

    report = bytes([0x03, 0x00, 0, 0, 0, 0, 0, 0])  # CTRL + SHIFT
    parsed = device.parse_input_report(report)

    curr = mapper.map(parsed[0])
    events = gen.diff(prev, curr)

    assert (ecodes.KEY_LEFTCTRL, 1) in {
        (e.code, e.value)
        for e in events
        if e.type == ecodes.EV_KEY
    }
    assert (ecodes.KEY_LEFTSHIFT, 1) in {
        (e.code, e.value)
        for e in events
        if e.type == ecodes.EV_KEY
    }
def test_linux_keyboard_duplicate_array_entries():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )


    prev = InputState()

    report = bytes([0x00, 0x00, 0x04, 0x04, 0, 0, 0, 0])  # A, A
    parsed = device.parse_input_report(report)

    curr = mapper.map(parsed[0])
    events = gen.diff(prev, curr)

    presses = [
        e for e in events
        if e.type == ecodes.EV_KEY and e.value == 1
    ]
    assert sum(1 for e in presses if e.code == ecodes.KEY_A) == 1
def test_linux_keyboard_key_replacement():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )

    report1 = bytes([0, 0, 0x04, 0, 0, 0, 0, 0])  # A
    report2 = bytes([0, 0, 0x05, 0, 0, 0, 0, 0])  # B

    parsed1 = device.parse_input_report(report1)
    parsed2 = device.parse_input_report(report2)

    state1 = mapper.map(parsed1[0])
    state2 = mapper.map(parsed2[0])

    events = gen.diff(state1, state2)

    assert any(e.code == ecodes.KEY_A and e.value == 0 for e in events)
    assert any(e.code == ecodes.KEY_B and e.value == 1 for e in events)

def test_linux_keyboard_array_clear_releases_all():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )


    report1 = bytes([0, 0, 0x04, 0x05, 0x06, 0, 0, 0])
    report2 = bytes([0] * 8)

    parsed1 = device.parse_input_report(report1)
    parsed2 = device.parse_input_report(report2)

    state1 = mapper.map(parsed1[0])
    state2 = mapper.map(parsed2[0])

    events = gen.diff(state1, state2)

    released = {
        e.code
        for e in events
        if e.type == ecodes.EV_KEY and e.value == 0
    }

    assert ecodes.KEY_A in released
    assert ecodes.KEY_B in released
    assert ecodes.KEY_C in released
def test_linux_keyboard_reserved_byte_ignored():
    device = get_test_device()
    mapper = HIDLinuxMapper()

    report = bytes([0, 0xFF, 0, 0, 0, 0, 0, 0])
    parsed = device.parse_input_report(report)
    print(parsed)
    state = mapper.map(parsed[0])
    print(state)
    assert all(v == 0 for v in state.keys.values())
def test_linux_keyboard_no_events_on_same_report():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0]
    )


    report = bytes([0, 0, 0x04, 0, 0, 0, 0, 0])

    parsed1 = device.parse_input_report(report)
    parsed2 = device.parse_input_report(report)

    state1 = mapper.map(parsed1[0])
    state2 = mapper.map(parsed2[0])

    events = gen.diff(state1, state2)

    assert events == []

def test_linux_keyboard_rollover_error():
    device = get_test_device()
    mapper = HIDLinuxMapper()
    gen = EventGenerator(
        supported_keys=mapper.get_supported_keys(device.fields)[0],
        supported_rel=[],
        abs_axis_info=mapper.get_abs_axis_info(device.fields)[0],
    )


    prev = InputState()

    report = bytes([0x00, 0x00, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01])
    parsed = device.parse_input_report(report)

    curr = mapper.map(parsed[0])
    events = gen.diff(prev, curr)

    key_events = [
        e for e in events
        if e.type == ecodes.EV_KEY
    ]

    # All key events must be presses (value == 1) - no releases
    assert all(e.value == 1 for e in key_events)
