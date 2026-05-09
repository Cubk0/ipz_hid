# ipz_hid

`ipz_hid` is a small Python package for working with HID report descriptors and HID reports in user space. It is intended mainly for educational experiments where the goal is to show the path from a HID report descriptor to parsed report data and Linux input events without writing a kernel driver.


## Installation

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The package requires Python 3.10 or newer and `evdev`.

On some systems, installing `evdev` from `pip` may need build tools and Python headers:

```bash
sudo apt install python3-dev build-essential
```

For real HID devices, the script needs access to `/dev/hidraw*` and sometimes `/dev/uinput`. During development it is simplest to run the selected Python interpreter with `sudo`:

```bash
sudo .venv/bin/python your_script.py
```

## Project structure

```text
src/ipz_hid/
├── core/
│   ├── descriptor.py       # HIDDescriptor and descriptor parsing from bytes
│   ├── device.py           # HIDDevice, descriptor interpretation, report parser setup
│   ├── field.py            # HIDField and report field parsing
│   ├── hid_helpers.py      # bit-level helper functions
│   ├── hid_items.py        # HID item classes, item tags, field attributes
│   ├── hid_types.py        # small data types used by parsed descriptors/reports
│   ├── hid_usages.py       # selected HID usage pages and usage constants
│   └── report_parser.py    # HIDReportParser
├── raw/
│   └── hid_raw.py          # low-level hidraw access
└── linux/
    ├── hid_linux_device.py # HIDDevice wrapper for Linux event generation
    ├── input_state.py      # input state and event diff generation
    ├── mapper.py           # HID usage to Linux input code mapping
    └── virtual_device.py   # optional uinput virtual device output
```

## Basic descriptor parsing

```python
from ipz_hid.core.descriptor import HIDDescriptor
from ipz_hid.core.device import HIDDevice

report_descriptor = bytes([...])
input_report = bytes([...])

descriptor = HIDDescriptor.from_bytes(report_descriptor)
device = HIDDevice()
device.set_descriptor(descriptor)

parsed = device.parse_input_report(input_report)
```


## Reading from a real hidraw device

```python
from ipz_hid.raw.hid_raw import HIDRaw

hidraw = HIDRaw.from_number(0)
hidraw.start()

try:
    report = hidraw.read()
finally:
    hidraw.close()
```

A device can also be selected by path or by matching its name in sysfs:

```python
hidraw = HIDRaw("/dev/hidraw0")
hidraw = HIDRaw.from_name("Pico")
```

## Linux event processing

```python
from ipz_hid.linux.hid_linux_device import HIDLinuxDevice, HIDLinuxDeviceOptions

options = HIDLinuxDeviceOptions(
    attach_hidraw=True,
    make_virtual_device=False,
    grab_events=False,
)

device = HIDLinuxDevice.from_device_path("/dev/hidraw0", options)
device.start()

try:
    report = device.read_input_report_raw()
    device.process_input_report(report)
    events = device.get_events()
finally:
    device.stop()
```

If `make_virtual_device=True`, parsed events are emitted through a virtual `uinput` device instead of being returned by `get_events()`.

If `grab_events=True`, the corresponding kernel event devices are grabbed with `EVIOCGRAB`. This prevents normal applications from receiving those input events while the program is running.

## Tests

Run tests from the project root:

```bash
python -m pytest
```

The tests cover descriptor parsing, report interpretation, mapping of HID usages to Linux input codes, and event generation from input state changes.

