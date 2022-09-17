
from pymem import pattern, Pymem
import sys
from time import sleep
"""https://github.com/Piotrekol/ProcessMemoryDataFinder/blob/95030bba9c5e2de0667c4ae95e6e6b1fbbde3d5c/OsuMemoryDataProvider/StructuredOsuMemoryReader.cs
https://github.com/Piotrekol/ProcessMemoryDataFinder/blob/95030bba9c5e2de0667c4ae95e6e6b1fbbde3d5c/OsuMemoryDataProvider/OsuMemoryModels/Direct/KeyOverlay.cs
Offset reference, every single [] bracket in syntax means you have to read_int() the value inside the brackets
"""
def pattern_scan_all(handle, patt, *, return_multiple=False):
    next_region = 0
    found = []
    user_space_limit = 0x7FFFFFFF0000 if sys.maxsize > 2**32 else 0x7fff0000
    while next_region < user_space_limit:
        next_region, page_found = pattern.scan_pattern_page(
            handle,
            next_region,
            patt,
            return_multiple=return_multiple
        )
        if not return_multiple and page_found:
            return page_found
        if page_found:
            found += page_found
    if not return_multiple:
        return None
    return found

def converter(given: str):
    return bytes(r'\x' + given.replace(' ', r'\x').replace(r'\x??', '.').lower(), 'utf-8')

def qr(address):
    return pm.read_int(address)

regular_ruleset_sign = "7D 15 A1 ?? ?? ?? ?? 85 C0"
base_sign = "F8 01 74 04 83 65"
different_ruleset_sign = "C7 86 48 01 00 00 01 00 00 00 A1"
pm = Pymem("osu!.exe")
address_rulesets = pattern_scan_all(pm.process_handle, converter(different_ruleset_sign), return_multiple=False)
address_base = pattern_scan_all(pm.process_handle, converter(base_sign), return_multiple=False)
print('address_rulesets', address_rulesets, '\naddress_base', address_base)
address_beatmap = pm.read_int(address_base - (0xC))
address_ruleset = qr(address_rulesets + (0xB)) + (0x4) # - (0xB) and not + (0xB) if used regular_ruleset_sign


keypress_classaddr = qr(qr(qr(qr(address_ruleset)+(0xa8))+(0x10))+(0x4))
key1_addr = qr(keypress_classaddr+(0x8))
key2_addr = qr(keypress_classaddr+(0xc))

for i in range(1000):
    sleep(0.02)
    print('how many key1 presses:', qr(key1_addr+(0x14)))
    print('is key1 pressed:', pm.read_bool(key1_addr + (0x1c)))
    print('is key2 pressed:',pm.read_bool(key1_addr + (0x1c)))
    print('how many key2 presses:', qr(key2_addr+(0x14)))
