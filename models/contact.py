from dataclasses import dataclass


@dataclass
class Contact:
    name: str
    lastName: str
    email: str
    phone: str
    address: str
    description: str

