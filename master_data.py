from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class Customer:
    global_id: str
    name: str
    email: str
    phone: Optional[str] = None

    @staticmethod
    def create(name, email, phone=None):
        return Customer(
            global_id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=phone
        )