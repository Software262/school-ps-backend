from datetime import datetime

from sqlmodel import Field, SQLModel


class Base(SQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime | None = Field(default=datetime.now, nullable=False)
    updated_at: datetime | None = Field(default=datetime.now, nullable=False)
