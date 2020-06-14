from bose import Packet, FunctionBlock, Operator, ProductInfoFunction


class BmapVersionGetPacket(Packet):
    def __init__(self) -> None:
        super().__init__(FunctionBlock.PRODUCT_INFO, ProductInfoFunction.BMAP_VERSION, Operator.GET)


class BmapVersionStatusPacket(Packet):
    @property
    def version(self):
        return self.payload.decode("utf-8")


MAP = {
    (ProductInfoFunction.BMAP_VERSION, Operator.STATUS): BmapVersionStatusPacket
}