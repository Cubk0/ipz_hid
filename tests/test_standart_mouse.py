from ipz_hid.core.descriptor import HIDDescriptor
from ipz_hid.core.device import HIDDevice
from ipz_hid.core.field import HIDField
from ipz_hid.core.hid_types import HIDInput, HIDInputField, HIDUsage
from ipz_hid.core.hid_items import *
from ipz_hid.core.hid_usages import *

descriptor = bytes([
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
    0x81, 0x02,        #     Input (Data, Variable, Absolute) ; Buttons

    0x95, 0x01,        #     Report Count (1)
    0x75, 0x05,        #     Report Size (5)
    0x81, 0x03,        #     Input (Constant) ; Padding

    0x05, 0x01,        #     Usage Page (Generic Desktop)
    0x09, 0x30,        #     Usage (X)
    0x09, 0x31,        #     Usage (Y)
    0x09, 0x38,        #     Usage (Wheel)
    0x15, 0x81,        #     Logical Minimum (-127)
    0x25, 0x7F,        #     Logical Maximum (127)
    0x75, 0x08,        #     Report Size (8)
    0x95, 0x03,        #     Report Count (3)
    0x81, 0x06,        #     Input (Data, Variable, Relative) ; X, Y, Wheel

    0xC0,              #   End Collection
    0xC0               # End Collection
])


def get_test_device() -> HIDDevice:
  device:HIDDevice= HIDDevice()
  device.set_descriptor(HIDDescriptor.from_bytes(descriptor));
  return device;

def test_parse_descriptor():
  device:HIDDevice= HIDDevice()
  device.set_descriptor(HIDDescriptor.from_bytes(descriptor));
  assert len(device.collections) == 2
  assert device.collections[0].usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.MOUSE)
  assert len(device.fields) == 3
  button_field:HIDField = device.fields[0]
  assert button_field.attributes.is_variable == True;
  assert button_field.attributes.is_constant == False;
  assert button_field.report_size == 1;
  assert button_field.report_count == 3;
  assert button_field.application_collection!=None
  assert button_field.logical_collection==None
  assert button_field.physical_collection!=None

  axes_field:HIDField = device.fields[2]
  assert axes_field.attributes.is_variable == True
  assert axes_field.attributes.is_constant == False
  assert axes_field.attributes.is_relative == True
  assert axes_field.report_size == 8
  assert axes_field.report_count == 3
  assert axes_field.logical_min == -127
  assert axes_field.logical_max == 127
  assert axes_field.application_collection!=None
  assert axes_field.logical_collection==None
  assert axes_field.physical_collection!=None

def test_parse_mouse():
  device:HIDDevice = get_test_device()
  # buttons: BUTTON_1 + BUTTON_3 pressed
  # dx = +5, dy = -3, wheel = +1
  report = bytes([
      0b00000101,  # Buttons: 1 + 3
      0x05,        # X
      0xFD,        # Y (-3)
      0x01         # Wheel
  ])
  parsed = device.parse_input_report(report)
  # Buttons field
  button_field:HIDInputField = parsed[0][0]
  assert button_field.field.application_collection is not None
  assert button_field.field.application_collection.usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.MOUSE)  
  assert button_field.field.application_collection.type == HIDCollectionType.APPLICATION
  buttons:list[HIDInput] = button_field.input_array
  assert buttons[0].usage == HIDUsage(UsagePage.BUTTON, ButtonUsage.BUTTON_1)
  assert buttons[2].usage == HIDUsage(UsagePage.BUTTON, ButtonUsage.BUTTON_3)
  # X axis
  axes_field:HIDInputField = parsed[0][1]
  assert axes_field.input_array[0].usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.X)
  assert axes_field.input_array[0].value == 5
  # Y axis
  assert axes_field.input_array[1].usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.Y)
  assert axes_field.input_array[1].value == -3
  # Wheel
  assert axes_field.input_array[2].usage == HIDUsage(UsagePage.GENERIC_DESKTOP, GenericDesktopUsage.WHEEL)
  assert axes_field.input_array[2].value == 1
