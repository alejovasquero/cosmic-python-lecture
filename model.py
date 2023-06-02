from typing import List

class Product:
    sku: str
    name: str
    description: str


class OrderLine:
    id: str
    product: Product
    quantity: int

    def __init__(self, id: str,  quantity: int, product=None):
        self.id = id
        self.product = product
        self.quantity = quantity

class Order:
    reference: str
    lines: List[OrderLine]

class Batch:
    reference: str
    sku: str
    quantity: int
    allocation: List[OrderLine]
    eta: str
    
    def __init__(self, reference: str, sku: str, quantity: int):
        self.reference = reference
        self.sku = sku
        self.quantity = quantity
        self.allocation = []
        self.eta = None

    def allocate(self, line: OrderLine):
        if self.quantity >= line.quantity:
            self.allocation.append(line)
            self.quantity -= line.quantity