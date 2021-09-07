from typing import List, Dict


class Product:
    product_asin: str
    parent_asin: str
    weight: float
    brand: str
    price_min: float
    price_max: float
    in_stock: bool
    stock: int
    ship_day_min: int
    ship_day_max: int
    ship: str
    delivery: str
    material: str
    description: list
    title: str
    size_length: str
    size_width: str
    size_height: str
    color: str
    variation_values: Dict[str, list]
    selected_variations: dict
    asin_variation_values: Dict[str, dict]

    def __init__(self, attrs=None):
        self.__dict__ = attrs or dict()

    def __str__(self):
        return str(self.__dict__)
