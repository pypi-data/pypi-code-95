from typing import Dict, Optional

from pydantic import BaseModel


class Product(BaseModel):
    product_asin: Optional[str]
    parent_asin: Optional[str]
    weight: Optional[float]
    brand: Optional[str]
    price_min: Optional[float]
    price_max: Optional[float]
    in_stock: Optional[bool]
    stock: Optional[int]
    ship_day_min: Optional[int]
    ship_day_max: Optional[int]
    ship: Optional[str]
    delivery: Optional[str]
    material: Optional[str]
    description: Optional[list]
    title: Optional[str]
    size_length: Optional[str]
    size_width: Optional[str]
    size_height: Optional[str]
    color: Optional[str]
    variation_values: Optional[Dict[str, list]]
    selected_variations: Optional[dict]
    asin_variation_values: Optional[Dict[str, dict]]
