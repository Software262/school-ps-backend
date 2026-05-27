from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.musical_band.schemas.request import CreateInstrumentRequest


class MusicalBandService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def create_item(self, item_data: CreateInstrumentRequest):
        type_id = await self.repository.get_type_id_by_name("banda")

        if not type_id:
            return None

        if item_data.tipo_inventario_id != type_id:
            return None

        return await self.repository.create_item(item_data=item_data)
