import fcntl
import glob
import os
import array
import struct
import fcntl

#<linux/hidraw.h>
EVIOCGRAB = 0x40044590
HIDIOCGRDESCSIZE = 0x80044801  
HIDIOCGRDESC = 0x80184801
HID_MAX_DESCRIPTOR_SIZE = 4096

class HIDRaw:

    def __init__(self,dev_path: str):
        self.dev_path =dev_path
        self.dev_descriptor =self.get_hidraw_descriptor(dev_path)
        self.dev_file = None
        self.grabbed_event_fds = []

    @classmethod
    def from_number(cls,number :int):
        dev_path = f"/dev/hidraw{number}"
        return cls(dev_path)

    @classmethod
    def from_name(cls,name:str):
        for hidraw_path in glob.glob("/sys/class/hidraw/hidraw*"):
            uevent_path = os.path.join(hidraw_path, "device/uevent")
            try:
                with open(uevent_path, "r") as f:
                    data = f.read()
                    if name in data:
                        dev_node = "/dev/" + os.path.basename(hidraw_path)
                        return cls(dev_node)
            except FileNotFoundError:
                continue
        raise FileNotFoundError(f"HID device with name '{name}' not found")

    def start(self):
        self.dev_file = os.open(self.dev_path, os.O_RDWR)
    def read(self)->bytes:
        if self.dev_file is None:
            raise RuntimeError("Device not opened. Call start() first.")
        return os.read(self.dev_file, 4096)
    def write(self,out_report:bytes):
        if self.dev_file is None:
            raise RuntimeError("Device not opened. Call start() first.")
        os.write(self.dev_file, out_report)
    def get_hidraw_descriptor(self, dev_path: str) -> bytes:
        # First try hidraw ioctl
        try:
            fd = os.open(dev_path, os.O_RDONLY)
            try:
                size_buf = array.array('I', [0])
                fcntl.ioctl(fd, HIDIOCGRDESCSIZE, size_buf, True)
                desc_size = size_buf[0]

                if desc_size > HID_MAX_DESCRIPTOR_SIZE:
                    raise ValueError("Descriptor too large")

                buf = bytearray(4 + HID_MAX_DESCRIPTOR_SIZE)
                struct.pack_into("I", buf, 0, desc_size)

                fcntl.ioctl(fd, HIDIOCGRDESC, buf, True)

                return bytes(buf[4:4 + desc_size])
            finally:
                os.close(fd)

        except OSError:
            # Fallback to sysfs
            hidraw = os.path.basename(dev_path)
            sysfs_path = f"/sys/class/hidraw/{hidraw}/device/report_descriptor"

            with open(sysfs_path, "rb") as f:
                return f.read()


    def hidraw_to_event_devices(self) -> list[str]:
        if not self.dev_path.startswith("/dev/hidraw"):
            raise ValueError("Invalid hidraw device path")
        hidraw = os.path.basename(self.dev_path)
        base = f"/sys/class/hidraw/{hidraw}/device"

        event_nodes = []

        for input_dir in glob.glob(os.path.join(base, "input/input*")):
            for event in glob.glob(os.path.join(input_dir, "event*")):
                event_nodes.append("/dev/input/" + os.path.basename(event))

        return event_nodes
    def grab_all_events(self):
        event_devices = self.hidraw_to_event_devices()

        if not event_devices:
            raise RuntimeError("No event devices associated with hidraw device")
        for dev in event_devices:
            fd = os.open(dev, os.O_RDONLY)
            fcntl.ioctl(fd, EVIOCGRAB, 1)
            self.grabbed_event_fds.append(fd)
    def release(self):
        for fd in self.grabbed_event_fds:
            try:
                fcntl.ioctl(fd, EVIOCGRAB, 0)
            finally:
                os.close(fd)
        self.grabbed_event_fds.clear()

    def close(self):
        if self.dev_file is not None:
            os.close(self.dev_file)
            self.dev_file = None