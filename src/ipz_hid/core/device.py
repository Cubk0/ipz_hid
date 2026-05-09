from __future__ import annotations
from typing import Optional

from ipz_hid.core.hid_items import HIDCollectionType, HIDFieldAttributes, HIDGlobalTag, HIDItem, HIDItemType, HIDLocalTag, HIDMainTag
from ipz_hid.core.descriptor import HIDDescriptor
from ipz_hid.core.field import HIDField
from ipz_hid.core.hid_types import GlobalState, HIDCollection, HIDUsage
from ipz_hid.core.report_parser import HIDReportParser

class HIDDevice():
    def __init__(self):
        self.collections = []
        self.collection_index_stack = []
        self.fields:list[HIDField] = []
        self.input_report_parsers = {}
        self.output_report_parsers = {}
        self.feature_report_parsers = {} # TODO maybe not needed?
        self.global_state_stack = []
        self.global_state = GlobalState();
        self.local_usage_min = -1
        self.local_usage_min_usage_page = -1
        self.local_usage_max = -1
        self.local_usage_max_usage_page = -1
        self.local_usage_list = []
        self.using_report_ids = False
        self.top_level_collection_count = 0
        self.descriptor=None
    def _get_collection_with_type(self,collection:HIDCollection,collection_type:HIDCollectionType)-> Optional[HIDCollection]:
        if collection.type == collection_type:
            return collection
        while True:
            if collection.type == collection_type:
                return collection
            else:
                if(collection.parent_index==-1):
                    return None
                collection = self.collections[collection.parent_index]


        return None
    def _start_collection(self,usage:HIDUsage,type:HIDCollectionType):
        index = len(self.collections)
        new_collection = HIDCollection(usage,type,index)
        new_collection.parent_index = self.collection_index_stack[-1] if len(self.collection_index_stack)>0 else -1
        if(new_collection.parent_index== -1):
            new_collection.tlc_index = self.top_level_collection_count
            self.top_level_collection_count+=1
        else:
            new_collection.tlc_index = self.collections[new_collection.parent_index].tlc_index
        self.collections.append(new_collection)
        self.collection_index_stack.append(index)
    def _end_collection(self):
        if len(self.collection_index_stack)>0:
            self.collection_index_stack.pop()
        else:
            raise ValueError("Collection stack underflow")
    def _bytes_to_usage(self,usage_bytes:bytes)->HIDUsage:
       return HIDUsage(page=self.global_state.usage_page, usage=int.from_bytes(usage_bytes,'little') if len(usage_bytes)>0 else 0)
    def _parse_main(self,item:HIDItem):
        match item.item_tag:
            case HIDMainTag.COLLECTION:
                if len(self.local_usage_list) == 0:
                    raise ValueError("No usage defined for collection")
                usage = self.local_usage_list[0]

                if(len(self.local_usage_list)>1):
                    print("Warning: Multiple usages defined for collection, using first usage in list\n")
                self._start_collection(usage,HIDCollectionType(item.item_data[0]))
            case HIDMainTag.END_COLLECTION:
                self._end_collection()
            case HIDMainTag.INPUT | HIDMainTag.OUTPUT | HIDMainTag.FEATURE:
                if self.global_state.report_size == 0 or self.global_state.report_count == 0:
                    raise ValueError("Report size and count must be set before defining fields")
                attributes = HIDFieldAttributes.from_byte(item.item_data[0])
                new_field = HIDField(
                    device = self,
                    attributes=attributes,
                    collection=self.collections[self.collection_index_stack[-1]],
                    report_id= self.global_state.report_id,
                    tag = item.item_tag,
                    usage_table = self.local_usage_list.copy(),
                    report_size = self.global_state.report_size,
                    report_count = self.global_state.report_count,
                    logical_max = self.global_state.logical_max,
                    logical_min = self.global_state.logical_min,
                )
                self.fields.append(new_field)

        self.local_usage_max=-1;
        self.local_usage_min=-1;
        self.local_usage_min_usage_page=-1;
        self.local_usage_max_usage_page=-1;
        self.local_usage_min=-1;
        self.local_usage_list.clear()
    def _parse_global(self,item:HIDItem):
        match item.item_tag:
            case HIDGlobalTag.USAGE_PAGE:
                self.global_state.usage_page = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.LOGICAL_MINIMUM:
                self.global_state.logical_min = int.from_bytes(item.item_data,'little',signed=True) # TODO check signed
            case HIDGlobalTag.LOGICAL_MAXIMUM:
                self.global_state.logical_max = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.PHYSICAL_MINIMUM:
                self.global_state.physical_min = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.PHYSICAL_MAXIMUM:
                self.global_state.physical_max = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.UNIT_EXPONENT:
                self.global_state.unit_exponent = int.from_bytes(item.item_data,'little',signed=True)
            case HIDGlobalTag.UNIT:
                self.global_state.unit = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.REPORT_SIZE:
                self.global_state.report_size = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.REPORT_ID:
                self.global_state.report_id = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.REPORT_COUNT:
                self.global_state.report_count = int.from_bytes(item.item_data,'little')
            case HIDGlobalTag.PUSH:
                self.global_state_stack.append(self.global_state)
                self.global_state = GlobalState()
            case HIDGlobalTag.POP:
                if len(self.global_state_stack)>0:
                    self.global_state = self.global_state_stack.pop()
                else:
                    raise ValueError("Global state stack underflow")
    def _parse_local(self,item:HIDItem):
        match item.item_tag:
            case HIDLocalTag.USAGE:
                usage = self._bytes_to_usage(item.item_data)
                self.local_usage_list.append(usage)
            case HIDLocalTag.USAGE_MINIMUM:
                self.local_usage_min = int.from_bytes(item.item_data,'little')
                self.local_usage_min_usage_page = self.global_state.usage_page
            case HIDLocalTag.USAGE_MAXIMUM:
                self.local_usage_max = int.from_bytes(item.item_data,'little')
                if self.local_usage_min == -1:
                    raise ValueError("Usage maximum defined before usage minimum")
                if self.local_usage_min_usage_page != self.global_state.usage_page:
                    raise ValueError("Usage maximum usage page does not match usage minimum usage page")
                for u in range(self.local_usage_min,self.local_usage_max+1):
                    usage = HIDUsage(self.global_state.usage_page,u)
                    if usage not in self.local_usage_list:
                        self.local_usage_list.append(usage)
                self.local_usage_min=-1
                self.local_usage_min_usage_page=-1
                self.local_usage_max=-1
                self.local_usage_max_usage_page=-1
            case _:
                raise ValueError(f"Unsupported local tag {item.item_tag}")
    def set_descriptor(self,descriptor:HIDDescriptor):
        self.descriptor = descriptor
        if len(self.collections) !=0:
            self.collections = []
            self.collection_index_stack = []
            self.fields:list[HIDField] = []
            self.input_report_parsers = {}
            self.output_report_parsers = {}
            self.feature_report_parsers = {} # TODO maybe not needed?
            self.global_state_stack = []
            self.global_state = GlobalState();
            self.local_usage_min = -1
            self.local_usage_min_usage_page = -1
            self.local_usage_max = -1
            self.local_usage_max_usage_page = -1
            self.local_usage_list = []
            self.using_report_ids = False
            self.top_level_collection_count = 0
            self.descriptor=None
        for item in descriptor.items:
            match item.item_type:
                case HIDItemType.MAIN:
                    self._parse_main(item)
                case HIDItemType.GLOBAL:
                    self._parse_global(item)
                case HIDItemType.LOCAL:
                    self._parse_local(item)
                case _:
                    raise ValueError(f"Unsupported item type {item.item_type}")
        for field in self.fields:
            if field.report_id != -1:
                self.using_report_ids = True
            match field.tag:
                case HIDMainTag.INPUT:
                    if field.report_id not in self.input_report_parsers:
                        self.input_report_parsers[field.report_id] = HIDReportParser([])
                    else:
                        prev_field = self.input_report_parsers[field.report_id].fields[-1]
                        field.bit_offset = prev_field.bit_offset + prev_field.get_size_bits()
                    self.input_report_parsers[field.report_id].fields.append(field)
                case HIDMainTag.OUTPUT:
                    if field.report_id not in self.output_report_parsers:
                        self.output_report_parsers[field.report_id] = HIDReportParser([])
                    else:
                        prev_field = self.input_report_parsers[field.report_id].fields[-1]
                        field.bit_offset = prev_field.bit_offset + prev_field.get_size_bits()
                    self.output_report_parsers[field.report_id].fields.append(field)
                case HIDMainTag.FEATURE:
                    if field.report_id not in self.feature_report_parsers:
                        self.feature_report_parsers[field.report_id] = HIDReportParser([])
                    else:
                        prev_field = self.input_report_parsers[field.report_id].fields[-1]
                        field.bit_offset = prev_field.bitoffset + prev_field.get_size_bits()
                    self.feature_report_parsers[field.report_id].fields.append(field)
                case _:
                    raise ValueError(f"Unsupported field tag {field.tag}")
            if -1 in self.input_report_parsers and self.using_report_ids:
                raise ValueError("Report with no ID used while other reports have IDs\nPlease ensure all reports have IDs or none do")
    def get_descriptor(self):
        return self.descriptor
    def parse_input_report(self,report:bytes):
        if len(self.input_report_parsers) == 0:
            raise ValueError("No field defined in descriptor")
        if(self.using_report_ids):
            return self.input_report_parsers[report[0]].parse_report(report[1:])
        else:
            return self.input_report_parsers[-1].parse_report(report)
    def parse_output_report(self,report:bytes):
        if len(self.output_report_parsers) == 0:
            raise ValueError("No field defined in descriptor")
        if(self.using_report_ids):
            return self.output_report_parsers[report[0]].parse_report(report)
        else:
            return self.output_report_parsers[-1].parse_report(report)
