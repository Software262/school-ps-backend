from app.modules.chess.infrastructure.repository import ChessRepository
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import CreateBorrowRequest, ReturnBorrowRequest
from app.modules.chess.schemas.request import CreateChessBorrowRequest, ReturnChessBorrowRequest, ResolveChessNoveltyRequest
from app.modules.inventory.infrastructure.models import Novedad

class ChessService:
    def __init__(self, chess_repo: ChessRepository, inventory_repo: InventoryRepository):
        self.chess_repo = chess_repo
        self.inventory_repo = inventory_repo

    async def create_chess_borrow(self, data: CreateChessBorrowRequest):
        # Validation 1: Verify inventory item exists
        item = await self.inventory_repo.get_item_by_id(data.inventario_id)
        if not item:
            return {"error": "NOT_FOUND", "message": f"El ítem de inventario con ID {data.inventario_id} no existe en la base de datos."}
            
        # Case-insensitive type check
        from sqlmodel import select
        from app.modules.inventory.infrastructure.models import TipoInventario
        tipos = self.inventory_repo.session.exec(select(TipoInventario)).all()
        tipo_ajedrez = next((t for t in tipos if t.nombre.lower() == "ajedrez"), None)
        
        if not tipo_ajedrez:
            return {"error": "BAD_REQUEST", "message": "No existe una categoría llamada 'ajedrez' en la base de datos."}
            
        if item.tipo_inventario_id != tipo_ajedrez.id:
            return {"error": "BAD_REQUEST", "message": f"El ítem seleccionado (Categoría {item.tipo_inventario_id}) no pertenece a la categoría de ajedrez (ID {tipo_ajedrez.id})."}
            
        # Validation 2: Verify available stock
        if item.cantidad < data.cantidad:
            return {"error": "BAD_REQUEST", "message": f"No hay suficientes tableros disponibles. Solicitados: {data.cantidad}, Stock actual: {item.cantidad}"}

        # We need an estudiante_id for Inventory Prestamo, even if borrowing for a group
        # If not provided, we might have an issue with Inventory foreign key. We assume
        # the frontend passes a valid representative if grado_id is used.
        est_id = data.estudiante_id if data.estudiante_id else 1 # Fallback or logic here
        
        borrow_req = CreateBorrowRequest(
            inventario_id=data.inventario_id,
            estudiante_id=est_id,
            fecha_salida=data.fecha_salida,
            cantidad=data.cantidad,
            observacion=data.observacion
        )
        prestamo = await self.inventory_repo.create_borrow(borrow_req)

        # Store extension if grado_id was provided
        if data.grado_id:
            assert prestamo.id is not None
            self.chess_repo.create_borrowing_extension(prestamo_id=prestamo.id, grado_id=data.grado_id)  # type: ignore[arg-type]

        return prestamo

    async def return_chess_borrow(self, prestamo_id: int, user_id: int, data: ReturnChessBorrowRequest):
        prestamo = await self.inventory_repo.get_borrowing(prestamo_id)
        if not prestamo:
            return {"error": "NOT_FOUND", "message": "Prestamo no encontrado"}

        # Return in inventory
        return_req = ReturnBorrowRequest(
            inventario_id=prestamo.inventario_id,
            estudiante_id=prestamo.estudiante_id,
            cantidad=prestamo.cantidad,
            observacion=data.observacion or ""
        )
        await self.inventory_repo.return_borrow(prestamo_id, return_req)

        # Update items stock
        item = await self.inventory_repo.get_item_by_id(prestamo.inventario_id)
        if item:
            assert item.id is not None
            await self.inventory_repo.update_amount_item(item.id, item.cantidad + prestamo.cantidad)  # type: ignore[arg-type]

        novedad_creada = False
        if data.conteo_piezas < 32:
            faltantes = 32 - data.conteo_piezas
            motivo = f"Material incompleto: Faltan {faltantes} piezas de ajedrez."
            novedad = await self.inventory_repo.create_novedad(
                prestamo_id=prestamo_id,
                descripcion=motivo
            )
            # Create extension
            assert novedad.id is not None
            self.chess_repo.create_novelty_extension(novedad_id=novedad.id)  # type: ignore[arg-type]
            novedad_creada = True

        return {
            "data": {
                "id": prestamo_id,
                "estado_prestamo": False,
                "novedad_creada": novedad_creada,
                "mensaje": "Prestamo devuelto exitosamente, se creó novedad por piezas faltantes" if novedad_creada else "Prestamo devuelto exitosamente"
            }
        }

    async def resolve_chess_novelty(self, novedad_id: int, data: ResolveChessNoveltyRequest):
        # Update the Novedad in inventory
        novedad = self.inventory_repo.session.get(Novedad, novedad_id)
        if not novedad:
            return {"error": "NOT_FOUND", "message": "Novedad no encontrada"}

        novedad.resuelta = True
        self.inventory_repo.session.add(novedad)
        self.inventory_repo.session.commit()
        self.inventory_repo.session.refresh(novedad)

        # Get or create extension to record audit
        extension = self.chess_repo.get_novelty_extension(novedad_id)
        if not extension:
            extension = self.chess_repo.create_novelty_extension(novedad_id)
        
        extension.resuelta_por_id = data.usuario_auditoria_id
        extension.notas_resolucion = data.notas_resolucion
        self.chess_repo.session.add(extension)
        self.chess_repo.session.commit()
        self.chess_repo.session.refresh(extension)

        return {"data": {"id": novedad_id, "resuelta": True, "mensaje": "Novedad resuelta y auditada correctamente"}}

    async def get_clearance(self, estudiante_id: int):
        open_novelties = self.chess_repo.get_open_novelties_by_student(estudiante_id)
        if open_novelties:
            return {"paz_y_salvo": False, "message": "El estudiante tiene novedades abiertas de Ajedrez."}
        return {"paz_y_salvo": True, "message": "Estudiante a paz y salvo en Ajedrez."}
