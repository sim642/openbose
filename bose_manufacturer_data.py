import hashlib


def unextract_manufacturer_id(manufacturer_id: int, manufacturer_data: bytes) -> bytes:
    manufacturer_id_bytes = bytes([manufacturer_id & 0xFF, (manufacturer_id >> 8) & 0xFF])
    return manufacturer_id_bytes + manufacturer_data


def mac_hash(mac: bytes, data: bytes) -> bytes:
    new_data = data[:4] + mac + data[9:]
    hash_data = new_data.hex().upper().encode("utf-8")
    return hashlib.sha256(hash_data).digest()


def is_bose_device(mac: bytes, data: bytes) -> bool:
    partial_mac_hash = data[4:9]
    return partial_mac_hash in mac_hash(mac, data) # possibly ok implementation?
    # return partial_mac_hash.hex() in mac_hash(mac, data).hex() # official implementation via .hex()


# from bluez dbus
mac = bytes([0x4C, 0x87, 0x5D, 0x53, 0xF2, 0xCF])
manufacturer_id = 2305
manufacturer_data = bytes([113, 18, 177, 27, 65, 149, 232, 52, 213, 174, 45, 195, 82])

# reconstruct full manufacturer data
# bose doesn't use manufacturer id correctly
# data = bytes([1, 9, 113, 18, 177, 27, 65, 149, 232, 52, 213, 174, 45, 195, 82])
data = unextract_manufacturer_id(manufacturer_id, manufacturer_data)

print(is_bose_device(mac, data))