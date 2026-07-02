from dataclasses import dataclass
import enum
from typing import Any
from enum import Enum  as  SQLAlchemyEnum

class Role(enum.Enum):
    USER="user"
    AI="ai"

