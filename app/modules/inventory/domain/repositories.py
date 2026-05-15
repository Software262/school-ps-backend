from sqlmodel import select

from app.core.db import SessionDep
from app.modules.inventory.infrastructure.models import Inventario
from app.modules.inventory.schemas.request import CreateItemRequest

class InventoryRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_inventory(self):
        return self.session.exec(select(Inventario)).all()
    
    async def create_item(self, item_data: CreateItemRequest):
        new_item = Inventario(
            tipo_inventario_id=item_data.tipo_inventario_id,
            nombre=item_data.nombre,
            cantidad=item_data.cantidad,
            estado_objeto=item_data.estado_objeto,
            observacion=item_data.observacion
        )
        self.session.add(new_item)
        self.session.commit()
        self.session.refresh(new_item)
        
        return new_item

