from dataclasses import dataclass
from typing import List


@dataclass
class HubPayment:
    external_id: str
    acquirer_transaction_id: str
    method: str
    credit_installments: int
    credit_card_brand: str
    credit_card_last_digits: str
    coupon_code: str
    value: float

@dataclass
class HubItem:
    external_id: str
    sku_code: str
    product_code: str
    quantity: int
    total_amount: float
    shipping_amount: float
    discount_amount: float
    image_url: str
    name: str
    unit_amount: float
    position: int

@dataclass
class HubInvoice:
    external_id: str
    number: str
    serie: str
    key: str
    date: str
    pdf: str
    xml: str

@dataclass
class HubShipping:
    external_id: str
    method: str
    tracking_url: str
    tracking_code: str
    delivery_estimate_date: str

@dataclass
class HubAddress:
    external_id: str
    receiver_name: str
    zip_code: str
    street: str
    number: str
    neighborhood: str
    complement: str
    city: str
    state: str
    country: str
    reference: str

@dataclass
class HubCustomer:
    external_id: str
    name: str
    corporate_trade_name: str
    corporate_ie: str
    email: str
    type: str
    document: str
    phone: str

@dataclass
class HubDelivery:
    external_id: str
    date: str

@dataclass
class HubOrder:
    date: str
    external_id: str
    items_amount: int
    shipping_amount: float
    discount_amount: float
    total_amount: float
    status: str
    invoice: HubInvoice
    shipping: HubShipping
    delivery: HubDelivery
    address: HubAddress
    customer: HubCustomer
    items: List[HubItem]
    payments = List[HubPayment]
    json: str
