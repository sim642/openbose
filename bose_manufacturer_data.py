import hashlib
import enum


class ProductType(enum.IntEnum):
    HEADPHONES = 0
    SPEAKER = 1


class ManufacturerData:
    data: bytes

    def __init__(self, data: bytes) -> None:
        self.data = data

    @classmethod
    def unextract_manufacturer_id(cls, manufacturer_id, manufacturer_data):
        manufacturer_id_bytes = bytes([manufacturer_id & 0xFF, (manufacturer_id >> 8) & 0xFF])
        return manufacturer_id_bytes + manufacturer_data

    @classmethod
    def from_manufacturer_id(cls, manufacturer_id: int, manufacturer_data: bytes) -> "ManufacturerData":
        data = cls.unextract_manufacturer_id(manufacturer_id, manufacturer_data)
        return ManufacturerData(data)

    @property
    def product_id(self) -> int:
        return self.data[1]

    @property
    def variant_id(self) -> int:
        return self.data[2] & 0x0F

    def get_bit(self, i: int, bit: int) -> bool:
        return bool((self.data[i] >> bit) & 0x01)

    @property
    def device1_connected(self) -> bool:
        return self.get_bit(2, 4)

    @property
    def device2_connected(self) -> bool:
        return self.get_bit(2, 5)

    @property
    def in_pairing_mode(self) -> bool:
        return self.get_bit(2, 7)

    @property
    def in_music_share(self) -> bool:
        return self.get_bit(3, 0)

    @property
    def supports_music_sharing(self) -> bool:
        return self.get_bit(3, 1)

    @property
    def product_type(self) -> ProductType:
        return ProductType(self.get_bit(3, 2))

    @property
    def partial_mac_hash(self) -> bytes:
        return self.data[4:9]

    @property
    def device1_mac(self) -> bytes:
        return self.data[9:12]

    @property
    def device2_mac(self) -> bytes:
        return self.data[12:15]


class MacManufacturerData(ManufacturerData):
    mac: bytes

    def __init__(self, mac: bytes, data: bytes) -> None:
        super().__init__(data)
        self.mac = mac

    @classmethod
    def from_manufacturer_id(cls, mac: bytes, manufacturer_id: int, manufacturer_data: bytes) -> "MacManufacturerData":
        data = cls.unextract_manufacturer_id(manufacturer_id, manufacturer_data)
        return MacManufacturerData(mac, data)

    @property
    def mac_hash(self):
        new_data = self.data[:4] + self.mac + self.data[9:]
        hash_data = new_data.hex().upper().encode("utf-8")
        return hashlib.sha256(hash_data).digest()

    @property
    def is_bose_device(self) -> bool:
        return self.partial_mac_hash in self.mac_hash  # possibly ok implementation?
        # return self.partial_mac_hash.hex() in self.mac_hash.hex() # official implementation via .hex()


# from bluez dbus
mac = bytes([0x4C, 0x87, 0x5D, 0x53, 0xF2, 0xCF])
manufacturer_id = 2305
manufacturer_data = bytes([113, 18, 177, 27, 65, 149, 232, 52, 213, 174, 45, 195, 82])
# manufacturer_data = bytes([113, 18, 108, 232, 1, 113, 93, 45, 195, 82, 52, 213, 174])

# reconstruct full manufacturer data
# bose doesn't use manufacturer id correctly
# data = bytes([1, 9, 113, 18, 177, 27, 65, 149, 232, 52, 213, 174, 45, 195, 82])
md = MacManufacturerData.from_manufacturer_id(mac, manufacturer_id, manufacturer_data)

print("is_bose_device:", md.is_bose_device)
print("product_id:", md.product_id)
print("variant_id:", md.variant_id)
print("product_type:", md.product_type)
print("device1_connected:", md.device1_connected)
print("device1_mac:", md.device1_mac.hex(sep=":"))
print("device2_connected:", md.device2_connected)
print("device2_mac:", md.device2_mac.hex(sep=":"))