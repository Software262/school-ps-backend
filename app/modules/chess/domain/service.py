from app.modules.chess.infrastructure.repository import ChessRepository
from app.modules.chess.schemas.request import (
    CreateChessBorrowRequest,
    ResolveBorrowNoveltyRequest,
    ResolveChessNoveltyRequest,
    ReturnChessBorrowRequest,
    CreateChessItemRequest,
)
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    ReturnBorrowRequest,
)


class ChessService:
    def __init__(
        self, chess_repo: ChessRepository, inventory_repo: InventoryRepository
    ):
        self.chess_repo = chess_repo
        self.inventory_repo = inventory_repo

    async def create_chess_item(self, item_data: CreateChessItemRequest):
        tipo_ajedrez = await self.inventory_repo.get_type_by_name("ajedrez")
        if not tipo_ajedrez:
            return {
                "error": "BAD_REQUEST",
                "message": "No existe una categoría llamada 'ajedrez' en la base de datos.",
            }

        if item_data.tipo_inventario_id != tipo_ajedrez.id:
            return {
                "error": "BAD_REQUEST",
                "message": "El tipo de inventario especificado no corresponde a ajedrez.",
            }

        # Embed pieces in the observation
        obs = f"[PIEZAS:{item_data.piezas_totales}]"
        if item_data.observacion:
            obs += f" {item_data.observacion}"

        req = CreateItemRequest(
            tipo_inventario_id=item_data.tipo_inventario_id,
            nombre=item_data.nombre,
            cantidad_total=item_data.cantidad_total,
            observacion=obs,
        )

        return await self.inventory_repo.create_item(req)

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

        if not item.id:
            return {
                "error": "BAD_REQUEST",
                "message": "El ítem de inventario no tiene un ID válido.",
            }

        available_state_id = await self.inventory_repo.get_state_id_by_name(
            "disponible"
        )
        if not available_state_id:
            return {
                "error": "BAD_REQUEST",
                "message": "No existe el estado 'disponible' en la base de datos.",
            }

        inventory_available_stock = await self.inventory_repo.get_inventory_stock(
            state_id=available_state_id,
            item_id=item.id,
        )
        if not inventory_available_stock:
            return {
                "error": "BAD_REQUEST",
                "message": "No hay stock disponible para este artículo.",
            }

        if inventory_available_stock.cantidad < data.cantidad:
            return {
                "error": "BAD_REQUEST",
                "message": f"No hay suficientes artículos disponibles. Solicitados: {data.cantidad}, Disponibles: {inventory_available_stock.cantidad}",
            }

        if not data.estudiante_id and not data.grado_id:
            return {
                "error": "BAD_REQUEST",
                "message": "Se debe especificar un estudiante_id o un grado_id",
            }

        est_id = data.estudiante_id or 0

        borrow_req = CreateBorrowRequest(
            inventario_id=data.inventario_id,
            estudiante_id=est_id,
            fecha_salida=data.fecha_salida,
            cantidad=data.cantidad,
            observacion=data.observacion,
        )

        # Move stock: disponible -> prestado
        borrow_state_id = await self.inventory_repo.get_state_id_by_name("prestado")
        if not borrow_state_id:
            return {
                "error": "BAD_REQUEST",
                "message": "No existe el estado 'prestado' en la base de datos.",
            }

        inventory_borrow_stock = await self.inventory_repo.get_inventory_stock(
            state_id=borrow_state_id,
            item_id=item.id,
        )

        await self.inventory_repo.set_amount_stock_category(
            item_id=item.id,
            amount=(inventory_available_stock.cantidad - data.cantidad),
            category_name="disponible",
        )

        if inventory_borrow_stock:
            await self.inventory_repo.set_amount_stock_category(
                item_id=item.id,
                amount=(inventory_borrow_stock.cantidad + data.cantidad),
                category_name="prestado",
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

        piezas_esperadas = 32
        if item and item.observacion and item.observacion.startswith("[PIEZAS:"):
            try:
                parts = item.observacion.split("]", 1)
                num_part = parts[0].replace("[PIEZAS:", "").strip()
                piezas_esperadas = int(num_part)
            except (ValueError, IndexError):
                pass

        novedad_creada = False
        target_category = "disponible"

        if data.conteo_piezas < piezas_esperadas:
            faltantes = piezas_esperadas - data.conteo_piezas
            motivo = f"Material incompleto: Faltan {faltantes} piezas de ajedrez."
            novedad = await self.inventory_repo.create_novedad(
                prestamo_id=prestamo_id, descripcion=motivo
            )
            if novedad.id is None:
                raise ValueError("La novedad creada no tiene un ID válido")
            self.chess_repo.create_novelty_extension(novedad_id=novedad.id)
            novedad_creada = True
            target_category = "mantenimiento"

        if item and item.id:
            # Move stock: prestado -> target_category (disponible or mantenimiento)
            type_target_id = await self.inventory_repo.get_state_id_by_name(
                target_category
            )
            type_borrowed_id = await self.inventory_repo.get_state_id_by_name(
                "prestado"
            )

            if type_target_id and type_borrowed_id:
                stock_target = await self.inventory_repo.get_inventory_stock(
                    state_id=type_target_id, item_id=item.id
                )
                stock_borrowed = await self.inventory_repo.get_inventory_stock(
                    state_id=type_borrowed_id, item_id=item.id
                )

                if stock_target and stock_borrowed:
                    await self.inventory_repo.set_amount_stock_category(
                        item_id=item.id,
                        amount=(stock_target.cantidad + prestamo.cantidad),
                        category_name=target_category,
                    )
                    await self.inventory_repo.set_amount_stock_category(
                        item_id=item.id,
                        amount=max(0, stock_borrowed.cantidad - prestamo.cantidad),
                        category_name="prestado",
                    )

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
                type_available_id = await self.inventory_repo.get_state_id_by_name(
                    "disponible"
                )
                type_maintenance_id = await self.inventory_repo.get_state_id_by_name(
                    "mantenimiento"
                )

                if type_available_id and type_maintenance_id:
                    stock_available = await self.inventory_repo.get_inventory_stock(
                        state_id=type_available_id, item_id=item.id
                    )
                    stock_maintenance = await self.inventory_repo.get_inventory_stock(
                        state_id=type_maintenance_id, item_id=item.id
                    )

                    if stock_available and stock_maintenance:
                        await self.inventory_repo.set_amount_stock_category(
                            item_id=item.id,
                            amount=(stock_available.cantidad + prestamo.cantidad),
                            category_name="disponible",
                        )
                        await self.inventory_repo.set_amount_stock_category(
                            item_id=item.id,
                            amount=max(
                                0, stock_maintenance.cantidad - prestamo.cantidad
                            ),
                            category_name="mantenimiento",
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
