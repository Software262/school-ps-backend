from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.core.db import engine
from app.modules import router

# import all models so SQLModel.metadata knows about every table
from app.modules.auth.infrastructure import models as _auth  # noqa: F401
from app.modules.cafeteria.infrastructure import models as _cafeteria  # noqa: F401
from app.modules.classroom.infrastructure import models as _classroom  # noqa: F401
from app.modules.enrollment.infrastructure import models as _enrollment  # noqa: F401
from app.modules.inventory.infrastructure import models as _inventory  # noqa: F401
from app.modules.peace_safe.infrastructure import models as _peace_safe  # noqa: F401
from app.modules.principal.infrastructure import models as _principal  # noqa: F401
from app.modules.tests.infrastructure import models as _tests  # noqa: F401
from app.modules.training_schools.infrastructure import models as _training_schools  # noqa: F401
from app.modules.tuition.infrastructure import models as _tuition  # noqa: F401

setttings = get_settings()

app = FastAPI()

# creates tables that do not yet exist; safe to run on an existing db
SQLModel.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[setttings.allow_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
