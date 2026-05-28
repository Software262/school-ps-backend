from datetime import datetime
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.chess.schemas.request import ReturnChessRequest


class ChessService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def return_chess_borrow(
        self, borrow_id: int, borrow_data: ReturnChessRequest
    ) -> dict:
        item = await self.repository.get_item_by_id(borrow_data.inventario_id)
        if not item or not item.id:
            return {
                "error": "NOT_FOUND",
                "message": f"El ítem con ID {borrow_data.inventario_id} no existe.",
            }

        borrow = await self.repository.get_borrowing(borrow_id)
        if not borrow:
            return {
                "error": "NOT_FOUND",
                "message": f"El préstamo con ID {borrow_id} no existe.",
            }

        if not borrow.estado_prestamo:
            return {
                "error": "BAD_REQUEST",
                "message": "Este material ya fue devuelto previamente.",
            }

        if (
            borrow.inventario_id != borrow_data.inventario_id
            or borrow.estudiante_id != borrow_data.estudiante_id
        ):
            return {
                "error": "BAD_REQUEST",
                "message": "Los datos no coinciden con el registro original.",
            }

        novedad_creada = False
        mensaje = "Material completo. Paz y Salvo liberado."

        borrow.fecha_devolucion = datetime.now()
        borrow.estado_prestamo = False
        borrow.observacion = borrow_data.observacion

        if borrow_data.piezas_devueltas < 32 or not borrow_data.reloj_funciona:
            item.cantidad = borrow_data.piezas_devueltas
            item.estado_objeto = (
                "Incompleto" if borrow_data.piezas_devueltas < 32 else "Dañado"
            )

            desc = f"Ajedrez - Piezas: {borrow_data.piezas_devueltas}/32. Reloj OK: {borrow_data.reloj_funciona}."
            await self.repository.create_novedad(borrow_id, desc)
            novedad_creada = True
            mensaje = "Material incompleto o dañado. Se exige reposición física. Paz y Salvo bloqueado."
        else:
            item.cantidad = 32
            item.estado_objeto = "Disponible"

        await self.repository.finalize_chess_return(borrow=borrow, item=item)

        return {
            "error": None,
            "data": {
                "id": borrow.id,
                "estado_prestamo": borrow.estado_prestamo,
                "novedad_creada": novedad_creada,
                "mensaje": mensaje,
            },
        }
