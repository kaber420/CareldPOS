from typing import Optional
from sqlmodel import Field, SQLModel

class Setting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True, index=True)
    value: str
    description: Optional[str] = None
    type: str = "string"  # string, boolean, number, json
    is_public: bool = Field(default=False)  # Whether this is visible to non-admins
