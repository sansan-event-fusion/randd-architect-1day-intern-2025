from dataclasses import dataclass


@dataclass
class Company:
    id: int
    name: str
    address: str
    phone: str
