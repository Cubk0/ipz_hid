from enum import IntEnum

from attr import dataclass

@dataclass
class HIDFieldAttributes:
    is_constant: bool = False
    is_variable: bool = False
    is_relative: bool = False
    is_wrap: bool = False
    is_non_linear:bool = False
    is_no_preferred:bool = False
    is_null_state:bool = False
    is_volatile:bool = False
    is_buffered_bytes:bool = False

    @classmethod
    def from_byte(cls,byte:int):
        attrs = cls()
        attrs.is_constant = (byte & 0b1) != 0
        attrs.is_variable = (byte & 0b10) != 0
        attrs.is_relative = (byte & 0b100) != 0
        attrs.is_wrap = (byte & 0b1000) != 0
        attrs.is_non_linear = (byte & 0b10000) != 0
        attrs.is_no_preferred = (byte & 0b100000) != 0
        attrs.is_null_state = (byte & 0b1000000) != 0
        attrs.is_volatile = (byte & 0b10000000) != 0
        attrs.is_buffered_bytes = (byte & 0b100000000) !=0
        return attrs
    def to_byte(self) -> bytes:
        byte = 0
        if self.is_constant:
            byte |= 0b1
        if self.is_variable:
            byte |= 0b10
        if self.is_relative:
            byte |= 0b100
        if self.is_wrap:
            byte |= 0b1000
        if self.is_non_linear:
            byte |= 0b10000
        if self.is_no_preferred:
            byte |= 0b100000
        if self.is_null_state:
            byte |= 0b1000000
        if self.is_volatile:
            byte |= 0b10000000
        if self.is_buffered_bytes:
            byte |= 0b100000000
        return byte.to_bytes(1,'little')
    def __str__(self):
        attrs = []
        if self.is_constant:
            attrs.append("Constant")
        if self.is_variable:
            attrs.append("Variable")
        if self.is_relative:
            attrs.append("Relative")
        if self.is_wrap:
            attrs.append("Wrap")
        if self.is_non_linear:
            attrs.append("NonLinear")
        if self.is_no_preferred:
            attrs.append("NoPreferred")
        if self.is_null_state:
            attrs.append("NullState")
        if self.is_volatile:
            attrs.append("Volatile")
        if self.is_buffered_bytes:
            attrs.append("BufferedBytes")
        return " | ".join(attrs) if len(attrs)>0 else "None"


 
class HIDCollectionType(IntEnum):
    PHYSICAL = 0x00
    APPLICATION = 0x01
    LOGICAL = 0x02
    REPORT = 0x03
    NAMED_ARRAY = 0x04
    USAGE_SWITCH = 0x05
    USAGE_MODIFIER = 0x06


class HIDItemType(IntEnum):
    MAIN = 0b00
    GLOBAL = 0b01
    LOCAL = 0b10
    RESERVED = 0b11


class HIDMainTag(IntEnum):
    INPUT = 0b1000
    OUTPUT = 0b1001
    FEATURE = 0b1011
    COLLECTION = 0b1010
    END_COLLECTION = 0b1100

class HIDGlobalTag(IntEnum):
    USAGE_PAGE = 0b0000
    LOGICAL_MINIMUM = 0b0001
    LOGICAL_MAXIMUM = 0b0010
    PHYSICAL_MINIMUM = 0b0011
    PHYSICAL_MAXIMUM = 0b0100 
    UNIT_EXPONENT = 0b0101
    UNIT = 0b0110
    REPORT_SIZE = 0b0111
    REPORT_ID = 0b1000
    REPORT_COUNT = 0b1001
    PUSH = 0b1010
    POP = 0b1011

class HIDLocalTag(IntEnum):
    USAGE = 0b0000
    USAGE_MINIMUM = 0b0001
    USAGE_MAXIMUM = 0b0010
    DESIGNATOR_INDEX = 0b0011
    DESIGNATOR_MINIMUM = 0b0100
    DESIGNATOR_MAXIMUM = 0b0101
    STRING_INDEX = 0b0111
    STRING_MINIMUM = 0b1000
    STRING_MAXIMUM = 0b1001
    DELIMITER = 0b1010


class HIDItem():
    def __init__(self,
                 item_type:IntEnum,
                 item_tag:IntEnum,
                 item_data :bytes= b""):
        self.item_type = item_type
        self.item_tag  = item_tag
        self.item_data = item_data
    @classmethod
    def from_bytes(cls,data:bytes):
        item_size =  int((data[0] & 0b11))
        item_size = item_size if item_size!=3 else 4
        if (item_size!= 0 and item_size!= 1 and item_size!= 2 and item_size!= 4):
            raise ValueError("HID item data size must be 0, 1, 2, or 4 bytes")
        to_ret = cls(HIDGlobalTag.PUSH,HIDGlobalTag.PUSH)
        to_ret.item_type = HIDItemType((data[0]>>2 & 0b11))
        int_tag = (data[0]>>4 & 0b1111)
        match to_ret.item_type:
            case HIDItemType.MAIN:
                to_ret.item_tag = HIDMainTag(int_tag)
            case HIDItemType.LOCAL:
                to_ret.item_tag = HIDLocalTag(int_tag)
            case HIDItemType.GLOBAL:
                to_ret.item_tag = HIDGlobalTag(int_tag) 

        to_ret.item_data = data[1:1+item_size]
        return to_ret
    def __str__(self):
        return f"{self.item_type.name} {self.item_tag.name if self.item_tag is not None else 'UNKNOWN'} {self.item_data.hex()}"
    
class MainItem(HIDItem):
    def __init__(self, tag:HIDMainTag, data:bytes):
        super().__init__(HIDItemType.MAIN, tag, data)

class GlobalItem(HIDItem):
    def __init__(self, tag:HIDGlobalTag, data:bytes):
        super().__init__(HIDItemType.GLOBAL, tag, data)

class LocalItem(HIDItem):
    def __init__(self, tag:HIDLocalTag, data:bytes):
        super().__init__(HIDItemType.LOCAL, tag, data)


# Main items
class InputItem(MainItem):
    def __init__(self, attributes: HIDFieldAttributes):
        super().__init__(HIDMainTag.INPUT, attributes.to_byte())
        self.value = attributes

class OutputItem(MainItem):
    def __init__(self, attributes: HIDFieldAttributes):
        super().__init__(HIDMainTag.OUTPUT, attributes.to_byte())
        self.value = attributes

class FeatureItem(MainItem):
    def __init__(self, attributes: HIDFieldAttributes):
        super().__init__(HIDMainTag.FEATURE, attributes.to_byte())
        self.value = attributes

class CollectionItem(MainItem):
    def __init__(self, collection_type: HIDCollectionType):
        data = collection_type.value.to_bytes(1,'little')
        super().__init__(HIDMainTag.COLLECTION, data)
        self.collection_type = collection_type

class EndCollectionItem(MainItem):
    def __init__(self):
        super().__init__(HIDMainTag.END_COLLECTION, b"")

# Global items

class UsagePageItem(GlobalItem):
    def __init__(self, usage_page: int):
        super().__init__(HIDGlobalTag.USAGE_PAGE, usage_page.to_bytes(2,'little'))
        self.usage_page = usage_page

class LogicalMinItem(GlobalItem):
    def __init__(self, value: int, size: int = 4):
        super().__init__(HIDGlobalTag.LOGICAL_MINIMUM, value.to_bytes(size, 'little', signed=True))
        self.value = value

class LogicalMaxItem(GlobalItem):
    def __init__(self, value: int, size: int = 4):
        super().__init__(HIDGlobalTag.LOGICAL_MAXIMUM, value.to_bytes(size, 'little', signed=True))
        self.value = value

class PhysicalMinItem(GlobalItem):
    def __init__(self, value: int, size: int = 4):
        super().__init__(HIDGlobalTag.PHYSICAL_MINIMUM, value.to_bytes(size, 'little', signed=True))
        self.value = value

class PhysicalMaxItem(GlobalItem):
    def __init__(self, value: int, size: int = 4):
        super().__init__(HIDGlobalTag.PHYSICAL_MAXIMUM, value.to_bytes(size, 'little', signed=True))
        self.value = value

class UnitExponentItem(GlobalItem):
    def __init__(self, value: int):
        super().__init__(HIDGlobalTag.UNIT_EXPONENT, value.to_bytes(1, 'little', signed=True))
        self.value = value

class UnitItem(GlobalItem):
    def __init__(self, value: int):
        super().__init__(HIDGlobalTag.UNIT, value.to_bytes(4, 'little'))
        self.value = value

class ReportSizeItem(GlobalItem):
    def __init__(self, value: int):
        super().__init__(HIDGlobalTag.REPORT_SIZE, value.to_bytes(1, 'little'))
        self.value = value

class ReportIDItem(GlobalItem):
    def __init__(self, value: int):
        super().__init__(HIDGlobalTag.REPORT_ID, value.to_bytes(1, 'little'))
        self.value = value

class ReportCountItem(GlobalItem):
    def __init__(self, value: int):
        super().__init__(HIDGlobalTag.REPORT_COUNT, value.to_bytes(1, 'little'))
        self.value = value

class PushItem(GlobalItem):
    def __init__(self):
        super().__init__(HIDGlobalTag.PUSH, b"")

class PopItem(GlobalItem):
    def __init__(self):
        super().__init__(HIDGlobalTag.POP, b"")

# Local items
class UsageItem(LocalItem):
    def __init__(self, usage: int):
        super().__init__(HIDLocalTag.USAGE, usage.to_bytes(2, 'little'))
        self.usage = usage

class UsageMinimumItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.USAGE_MINIMUM, value.to_bytes(2, 'little'))
        self.value = value

class UsageMaximumItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.USAGE_MAXIMUM, value.to_bytes(2, 'little'))
        self.value = value

class DesignatorIndexItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.DESIGNATOR_INDEX, value.to_bytes(1,'little'))
        self.value = value

class DesignatorMinimumItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.DESIGNATOR_MINIMUM, value.to_bytes(1,'little'))
        self.value = value

class DesignatorMaximumItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.DESIGNATOR_MAXIMUM, value.to_bytes(1,'little'))
        self.value = value

class StringIndexItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.STRING_INDEX, value.to_bytes(1,'little'))
        self.value = value

class StringMinimumItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.STRING_MINIMUM, value.to_bytes(1,'little'))
        self.value = value

class StringMaximumItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.STRING_MAXIMUM, value.to_bytes(1,'little'))
        self.value = value

class DelimiterItem(LocalItem):
    def __init__(self, value: int):
        super().__init__(HIDLocalTag.DELIMITER, value.to_bytes(1,'little'))
        self.value = value
