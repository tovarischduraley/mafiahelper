from abc import ABC

from pydantic import BaseModel


class BaseEntity(BaseModel, ABC):
    id: int

    def __hash__(self) -> str:
        return hash(self.id)

    def __eq__(self, other: "BaseEntity") -> bool:
        if type(self) is not type(other):
            return False
        return self.id == other.id
