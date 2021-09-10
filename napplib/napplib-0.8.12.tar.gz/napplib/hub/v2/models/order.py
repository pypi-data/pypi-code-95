from dataclasses import dataclass
from typing import List
from enum import Enum


@dataclass
class HubOrderPayment:
    external_id: str
    acquirer_transaction_id: str
    method: str
    credit_installments: int
    credit_card_brand: str
    credit_card_last_digits: str
    coupon_code: str
    value: float

@dataclass
class HubOrderItem:
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
class HubOrderInvoice:
    external_id: str
    number: str
    serie: str
    key: str
    date: str
    pdf: str
    xml: str

@dataclass
class HubOrderShipping:
    external_id: str
    method: str
    tracking_url: str
    tracking_code: str
    delivery_estimate_date: str

@dataclass
class HubOrderAddress:
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
class HubOrderCustomer:
    external_id: str
    name: str
    corporate_trade_name: str
    corporate_ie: str
    email: str
    type: str
    document: str
    phone: str

@dataclass
class HubOrderDelivery:
    external_id: str
    date: str

class HubOrderStatus(Enum):
    CREATING = "CREATING"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_APPROVED = "PAYMENT_APPROVED"
    INVOICED = "INVOICED"
    SHIPMENT = "SHIPMENT"
    DELIVERED = "DELIVERED"
    CANCELED = "CANCELED"


@dataclass
class HubOrder:
    date: str
    external_id: str
    items_amount: int
    shipping_amount: float
    discount_amount: float
    total_amount: float
    status: HubOrderStatus
    invoice: HubOrderInvoice
    shipping: HubOrderShipping
    delivery: HubOrderDelivery
    address: HubOrderAddress
    customer: HubOrderCustomer
    items: List[HubOrderItem]
    payments = List[HubOrderPayment]
    json: str
