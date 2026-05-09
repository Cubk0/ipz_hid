from __future__ import annotations

from ipz_hid.core.hid_items import HIDItem, HIDMainTag

class HIDDescriptor():
    def __init__(self,items: list[HIDItem] = []):
        self.items = items
    @classmethod
    def from_bytes(cls,data:bytes):
        index =0
        items=[]
        while (index < len(data)):
            item = HIDItem.from_bytes(data[index:])
            items.append(item)
            index += 1 + len(item.item_data)
        return cls(items)
    def __str__(self):
        res= ""
        indentation = 0;
        for item in self.items:
            if item.item_tag == HIDMainTag.END_COLLECTION:
                indentation -=1
            res += indentation* "  " +str(item) + "\n"
            if item.item_tag == HIDMainTag.COLLECTION:
                indentation +=1
        return res;
