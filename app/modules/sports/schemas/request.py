from app.modules.inventory.schemas.request import CreateItemRequest


# Reutilizamos todos los schemas de inventory directamente.
# Solo CreateSportItemRequest tiene alias propio para claridad en Swagger.
class CreateSportItemRequest(CreateItemRequest):
    """Schema para crear un item de deportes.
    El campo tipo_inventario_id debe corresponder al id del tipo 'deportes'.
    """

    pass
