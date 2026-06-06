from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.musical_band.schemas.request import (
    CreateInstrumentBorrowingMusicalBand,
    CreateInstrumentRequest,
    ReturnInstrumentBorrowingMusicalBand,
    UpdateItemMusicalBand,
)


class MusicalBandService(InventoryService):
    def __init__(self, repository: InventoryRepository):
        super().__init__(repository=repository)

    async def validate_musical_band(self, item_id: int):
        type_id = await self.repository.get_type_id_by_name("banda")

        if not type_id:
            return False

        if item_id != type_id:
            return False

        return True

    async def _create_item(self, item_data: CreateInstrumentRequest):
        valid = await self.validate_musical_band(item_id=item_data.tipo_inventario_id)

        if not valid:
            return None

        return await self.create_item(item_data=item_data)

    async def _update_item(self, item_id: int, item_data: UpdateItemMusicalBand):
        item = await self.repository.get_item_by_id(item_id=item_id)

        if not item:
            return None

        valid = await self.validate_musical_band(item_id=item.tipo_inventario_id)

        if not valid:
            return None

        item_data.tipo_inventario_id = item.tipo_inventario_id

        return await self.edit_item(item_id=item_id, item_data=item_data)

    async def create_borrowing(self, borrow_data: CreateInstrumentBorrowingMusicalBand):
        item = await self.repository.get_item_by_id(item_id=borrow_data.inventario_id)

        if not item:
            return None

        valid = await self.validate_musical_band(item_id=item.tipo_inventario_id)

        if not valid:
            return None

        return await self.create_borrow(borrow_data=borrow_data)

    async def return_borrowing(
        self, borrow_id: int, borrow_data: ReturnInstrumentBorrowingMusicalBand
    ):
        item = await self.repository.get_item_by_id(item_id=borrow_data.inventario_id)

        if not item:
            return None

        valid = await self.validate_musical_band(item_id=item.tipo_inventario_id)

        if not valid:
            return None

        return await self.return_borrow(borrow_id=borrow_id, borrow_data=borrow_data)
