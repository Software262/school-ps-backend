from app.modules.chess.infrastructure.repository import ChessRepository
from app.modules.chess.schemas.request import (
    CreateChessBorrowRequest,
    ResolveBorrowNoveltyRequest,
    ResolveChessNoveltyRequest,
    ReturnChessBorrowRequest,
)
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    ReturnBorrowRequest,
)


class ChessService:
    def __init__(
        self, chess_repo: ChessRepository, inventory_repo: InventoryRepository
    ):
        self.chess_repo = chess_repo
        self.inventory_repo = inventory_repo

    async def create_chess_borrow(self, data: CreateChessBorrowRequest):
        item = await self.inventory_repo.get_item_by_id(data.inventario_id)
        if not item:
            return {
                "error": "NOT_FOUND",
                "message": f"El ítem de inventario con ID {data.inventario_id} no existe en la base de datos.",
            }

        tipo_ajedrez = await self.inventory_repo.get_type_by_name("ajedrez")
        if not tipo_ajedrez:
            return {
                "error": "BAD_REQUEST",
                "message": "No existe una categoría llamada 'ajedrez' en la base de datos.",
            }

        if item.tipo_inventario_id != tipo_ajedrez.id:
            return {
                "error": "BAD_REQUEST",
                "message": f"El ítem seleccionado (Categoría {item.tipo_inventario_id}) no pertenece a la categoría de ajedrez (ID {tipo_ajedrez.id}).",
            }

        if item.cantidad_total < data.cantidad:
            return {
                "error": "BAD_REQUEST",
                "message": f"No hay suficientes tableros disponibles. Solicitados: {data.cantidad}, Stock actual: {item.cantidad_total}",
            }

        est_id = data.estudiante_id if data.estudiante_id else 1

        borrow_req = CreateBorrowRequest(
            inventario_id=data.inventario_id,
            estudiante_id=est_id,
            fecha_salida=data.fecha_salida,
            cantidad=data.cantidad,
            observacion=data.observacion,
        )
        prestamo = await self.inventory_repo.create_borrow(borrow_req)

        if data.grado_id:
            if prestamo.id is None:
                raise ValueError("El préstamo no tiene un ID válido después de crearlo")
            self.chess_repo.create_borrowing_extension(
                prestamo_id=prestamo.id, grado_id=data.grado_id
            )

        return prestamo

    async def return_chess_borrow(
        self, prestamo_id: int, user_id: int, data: ReturnChessBorrowRequest
    ):
        prestamo = await self.inventory_repo.get_borrowing(prestamo_id)
        if not prestamo:
            return {"error": "NOT_FOUND", "message": "Prestamo no encontrado"}

        return_req = ReturnBorrowRequest(
            inventario_id=prestamo.inventario_id,
            estudiante_id=prestamo.estudiante_id,
            cantidad=prestamo.cantidad,
            observacion=data.observacion or "",
        )
        await self.inventory_repo.return_borrow(prestamo_id, return_req)

        item = await self.inventory_repo.get_item_by_id(prestamo.inventario_id)
        if item:
            if item.id is None:
                raise ValueError("El item de inventario no tiene un ID válido")
            await self.inventory_repo.update_amount_item(
                item.id, item.cantidad_total + prestamo.cantidad
            )

        novedad_creada = False
        if data.conteo_piezas >= 32 and item and item.id:
            await self.inventory_repo.update_item_estado(
                item.id,
                "Disponible",
            )

        if data.conteo_piezas < 32:
            faltantes = 32 - data.conteo_piezas
            motivo = f"Material incompleto: Faltan {faltantes} piezas de ajedrez."
            novedad = await self.inventory_repo.create_novedad(
                prestamo_id=prestamo_id, descripcion=motivo
            )
            if novedad.id is None:
                raise ValueError("La novedad creada no tiene un ID válido")
            self.chess_repo.create_novelty_extension(novedad_id=novedad.id)
            novedad_creada = True

        return {
            "data": {
                "id": prestamo_id,
                "estado_prestamo": False,
                "novedad_creada": novedad_creada,
                "mensaje": "Prestamo devuelto exitosamente, se creó novedad por piezas faltantes"
                if novedad_creada
                else "Prestamo devuelto exitosamente",
            }
        }

    async def resolve_chess_novelty(
        self, novedad_id: int, data: ResolveChessNoveltyRequest
    ):
        novedad = self.chess_repo.get_novedad_by_id(novedad_id)
        if not novedad:
            return {"error": "NOT_FOUND", "message": "Novedad no encontrada"}

        self.chess_repo.resolve_novedad_and_extension(
            novedad=novedad,
            resuelta_por_id=data.usuario_auditoria_id,
            notas_resolucion=data.notas_resolucion,
        )

        return {
            "data": {
                "id": novedad_id,
                "resuelta": True,
                "mensaje": "Novedad resuelta y auditada correctamente",
            }
        }

    async def resolve_borrow_novelty(
        self, prestamo_id: int, data: ResolveBorrowNoveltyRequest
    ):
        novedad = await self.inventory_repo.get_novedad_by_borrow_id(prestamo_id)
        if not novedad:
            return {
                "error": "NOT_FOUND",
                "message": "No se encontró novedad para este préstamo.",
            }

        if novedad.resuelta:
            return {
                "error": "BAD_REQUEST",
                "message": "La novedad ya fue resuelta previamente.",
            }

        if novedad.id is None:
            raise ValueError("La novedad no tiene un ID válido")

        self.chess_repo.resolve_novedad_and_extension(
            novedad=novedad,
            resuelta_por_id=data.usuario_auditoria_id,
            notas_resolucion=data.notas_resolucion,
        )

        await self.inventory_repo.update_borrow_observacion(
            prestamo_id=prestamo_id,
            observacion="Devuelto completo en buen estado",
        )

        prestamo = await self.inventory_repo.get_borrowing(prestamo_id)
        if prestamo:
            item = await self.inventory_repo.get_item_by_id(prestamo.inventario_id)
            if item and item.id:
                await self.inventory_repo.update_item_estado(
                    item.id,
                    "Disponible",
                )

        return {
            "data": {
                "id": prestamo_id,
                "mensaje": "Novedad resuelta. Material repuesto correctamente.",
            }
        }

    async def get_clearance(self, estudiante_id: int):
        open_novelties = self.chess_repo.get_open_novelties_by_student(estudiante_id)
        if open_novelties:
            return {
                "paz_y_salvo": False,
                "message": "El estudiante tiene novedades abiertas de Ajedrez.",
            }
        return {"paz_y_salvo": True, "message": "Estudiante a paz y salvo en Ajedrez."}
