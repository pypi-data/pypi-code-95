from enum import Enum

from mongoengine import *
from upswingutil.db.model import ProfileIDObject, GuestsModel


class Status(Enum):
    NO_SHOW = 'NoShow'
    DEPARTED = 'Departed'
    RESERVED = 'Reserved'
    CANCELLED = 'Cancelled'
    ARRIVED = 'Arrived'
    CONFIRMED = 'Confirmed'
    CREATED = 'Created'
    UNCONFIRMED = 'Unconfirmed'
    MAINTENANCE = 'Maintenance'
    IN_HOUSE = 'InHouse'


class ReservationIDObj(DynamicEmbeddedDocument):
    reservation = StringField()
    confirmation = StringField()
    globalId = StringField()


class AlvieReservationModel(DynamicEmbeddedDocument):
    comments = ListField(StringField())
    rating = DictField()


class ReservationGuestShort(DynamicEmbeddedDocument):
    idObj = EmbeddedDocumentField(ProfileIDObject)
    primary = BooleanField()
    arrivalTransport = DictField()
    departureTransport = DictField()
    birthDate = StringField()
    guest = ReferenceField(GuestsModel)


class ReservationGuestInfo(DynamicEmbeddedDocument):
    adults = IntField()
    children = IntField()
    infants = IntField()
    childBuckets = DictField()
    preRegistered = BooleanField()
    guest_list = EmbeddedDocumentListField(ReservationGuestShort)


class ReservationModel(DynamicDocument):
    meta = {'collection': 'reservations'}

    _id = StringField(required=True, primary_key=True)
    agent = StringField(required=True)
    alvie = EmbeddedDocumentField(AlvieReservationModel)
    arrivalDate = StringField(required=True)
    bookingInfo = DictField()
    callHistory = ListField(DictField())
    cancellation = ListField(DictField())
    comments = ListField(DictField())
    createBusinessDate = StringField()
    createDateTime = StringField()
    daily_activity = ListField(DictField())
    departureDate = StringField()
    eCertificates = ListField(DictField())
    expectedTimes = DictField()
    financeInfo = DictField()
    folioInformation = DictField()
    guestInfo = EmbeddedDocumentField(ReservationGuestInfo)
    guestLocators = DictField()
    hotelId = StringField(required=True)
    hotelName = StringField(required=True)
    idObj = EmbeddedDocumentField(ReservationIDObj)
    inventoryItems = DictField()
    linkedReservation = DictField()
    memberships = ListField(DictField())
    metaInfo = DictField()
    orgId = StringField()
    originalTimeSpan = DictField()
    packages = ListField(DictField())
    policies = DictField()
    preferences = ListField(DictField())
    roomStay = DictField()
    status = EnumField(Status, default=Status.CREATED, required=True)
