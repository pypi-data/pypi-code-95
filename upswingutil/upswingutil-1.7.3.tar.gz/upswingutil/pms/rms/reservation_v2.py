import json
from datetime import datetime

from upswingutil.db.model import ReservationModel, Status, ReservationGuestInfo, ReservationGuestShort, GuestsModel, \
    ReservationModelV2, GuestsModelV2
from upswingutil.resource import get_model_from_cloud_storage
from upswingutil.pms.rms import NAME, get_key, validate_key
from upswingutil.db import Mongodb, Firestore, MongodbV2
from upswingutil.schema import Token
import upswingutil as ul
import requests
import logging


def _get_status(status):
    if status == 'NoShow':
        return Status.NO_SHOW
    elif status == 'Departed':
        return Status.DEPARTED
    elif status == 'Reserved':
        return Status.RESERVED
    elif status == 'Cancelled':
        return Status.CANCELLED
    elif status == 'Arrived':
        return Status.IN_HOUSE
    elif status == 'Maintenance':
        return Status.MAINTENANCE
    elif status == 'Confirmed':
        return Status.CONFIRMED
    else:
        logging.error(f'Missing Status : {status}')
        return Status.UNCONFIRMED


def _create_reservation_id_obj(record) -> dict:
    return {
        'reservation': str(record.get('id')),
        'globalId': f"{record.get('agent')}-{record.get('orgId')}-{record.get('clientId')}-{record.get('id')}",
        'accountId': str(record.get('accountId')),
        'activityId': str(record.get('activityId')),
        'boatId': str(record.get('boatId')),
        'bookerContactId': str(record.get('bookerContactId')),
        'businessLostId': str(record.get('businessLostId')),
        'businessSegmentId': str(record.get('businessSegmentId')),
        'cancellationPolicyId': str(record.get('cancellationPolicyId')),
        'cancelledById': str(record.get('cancelledById')),
        'contactId': str(record.get('contactId')),
        'confirmedById': str(record.get('confirmedById')),
        'coordinator1Id': str(record.get('coordinator1Id')),
        'coordinator2Id': str(record.get('coordinator2Id')),
        'createdById': str(record.get('createdById')),
        'destinationCodeId': str(record.get('destinationCodeId')),
        'externalCancelId': str(record.get('externalCancelId')),
        'externalResId': str(record.get('externalResId')),
        'fixedResReasonId': str(record.get('fixedResReasonId')),
        'modifiedById': str(record.get('modifiedById')),
        'mealPlanId': str(record.get('mealPlanId')),
        'occupantId': str(record.get('occupantId')),
        'paymentModeId': str(record.get('paymentModeId')),
        'splitResId': str(record.get('splitResId')),
        'subResTypeId': str(record.get('subResTypeId')),
        'bookingSourceId': str(record.get('bookingSourceId')),
        'companyId': str(record.get('companyId')),
        'discountId': str(record.get('discountId')),
        'groupAllotmentId': str(record.get('groupAllotmentId')),
        'groupReservationId': str(record.get('groupReservationId')),
        'marketSegmentId': str(record.get('marketSegmentId')),
        'onlineConfirmationId': str(record.get('onlineConfirmationId')),
        'resTypeId': str(record.get('resTypeId')),
        'subMarketSegmentId': str(record.get('subMarketSegmentId')),
        'travelAgentId': str(record.get('travelAgentId')),
        'voucherId': str(record.get('voucherId')),
        'wholesalerId': str(record.get('wholesalerId')),
        'roomId': str(record.get('areaId')),
        'hotelId': str(record.get('clientId')),
        'categoryId': str(record.get('categoryId')),
        'rateTypeId': str(record.get('rateTypeId')),
    }


def _create_guest_id_obj(record) -> dict:
    return {
        'profile': str(record.get('id')),
        'corporateId': str(record.get('companyId'))
    }


def _get_geo_region(nationalID: int):
    result = 'unknown'
    try:
        mongo = Mongodb('upswing')
        region = mongo.get_collection('countries').find_one({"_id": nationalID}, {"region": 1})
        mongo.close_connection()
        result = region if region else 'unknown'
    except Exception as e:
        logging.error(f'Error getting geo region of nation {nationalID}')
        logging.error(e)
    finally:
        return result


def _generate_day_to_day_entry(record):
    _daily_activity = list()
    for index, item in enumerate(record.get('daily_rates')):
        _daily_activity.append({
            'date': item['stayDate'].split(' ')[0],
            'day_of_stay': index + 1,
            'roomType': record.get('categoryName'),
            'ratePlanCode': record.get('rateTypeName'),
            'roomId': record.get('areaId'),
            'roomName': record.get('areaName'),
            'rates': {
                'currency': item.get('currency'),
                'amountBeforeTax': item.get('rateAmount'),
                'exclusiveTax': item.get('exclusiveTax'),
                'discountAmount': item.get('discountAmount'),
                'additionalsAmount': item.get('additionalsAmount'),
                'dynamicAmount': item.get('dynamicAmount'),
                'linkedRateAdjustmentAmount': item.get('linkedRateAdjustmentAmount'),
                'packageAmount': item.get('packageAmount'),
                'rateTypeId': item.get('rateTypeId'),
                'xNightsDiscount': item.get('xNightsDiscount'),
                'totalRateAmount': item.get('totalRateAmount')
            },
            'revenue': {
                'accommodation': item.get('accommodation'),
                'accommodationTax': item.get('accommodationTax'),
                'accommodationGST': item.get('accommodationGST'),
                'foodAndBeverage': item.get('foodAndBeverage'),
                'foodAndBeverageTax': item.get('foodAndBeverageTax'),
                'foodAndBeverageGST': item.get('foodAndBeverageGST'),
                'other': item.get('other'),
                'otherTax': item.get('otherTax'),
                'otherGST': item.get('otherGST')
            },
            'guestCounts': {
                'adults': record.get('adults'),
                'children': record.get('children'),
                'infants': record.get('infants')
            }
        })
    return _daily_activity


def _transform_guest_profile(record):
    guest = GuestsModelV2(
        _id=str(record.get('id')),
        idObj=_create_guest_id_obj(record),
        profileType='Guest',
        title=record.get('title'),
        firstName=record.get('guestGiven'),
        lastName=record.get('guestSurname'),
        datesAndDurations={
            'birthDate': record.get('birthDate'),
            'anniversary': None
        },
        address={
            'addressLine1': record.get('addressLine1'),
            'addressLine2': record.get('addressLine2'),
            'addressLine3': record.get('addressLine3'),
            'countryId': record.get('countryId'),
            'nationalityId': record.get('nationalityId'),
            'state': record.get('state'),
            'town': record.get('town'),
            'postCode': record.get('postCode'),
        },
        contactInfo={
            'email': record.get('email'),
            'email2': record.get('email2'),
            'mobile': record.get('mobile'),
            'telephone': record.get('phoneAH'),
        },
        privacyInfo={
            'emailOptOut': record.get('emailOptOut'),
            'marketingOptOut': record.get('marketingOptOut'),
            'smsOptOut': record.get('smsOptOut'),
            'privacyOptIn': record.get('privacyOptIn'),
            'phoneOptOut': record.get('phoneOptOut'),
        },
        documents={
            'passportId': record.get('passportId'),
        },
        metaInfo={
            'notes': record.get('notes'),
            'languageSpokenId': record.get('languageSpokenId')
        },
        company={
          'companyId': record.get('companyId')
        },
        registeredProperty=str(record.get('propertyId')),
        auraRecordUpdatedOn=datetime.now(),
    )
    return guest


def _add_reservation_to_alvie(record):
    firestore_db = Firestore(app='alvie')
    user_email_list = [item["email"] for item in record.get('guests')]
    resv_info = {
        "_id": record.get("id"),
        "agent": record.get("agent"),
        "orgId": record.get("orgId"),
        "areaId": record.get("areaId"),
        "arrivalDate": record.get("arrivalDate"),
        "departureDate": record.get("departureDate"),
        "propertyId": record.get("propertyId"),
        "propertyName": record.get("propertyName"),
        "status": record.get("status"),
        "travelAgentId": record.get("travelAgentId"),
        "travelAgentName": record.get("travelAgentName")
    }
    logging.debug(f"Final reservation id : {record.get('id')}")
    for email in user_email_list:
        docs = firestore_db.get_collection('users').where("email", "==", email).stream()
        for doc in docs:
            logging.debug("loading reservation to alvie")
            firestore_db.get_collection(f'users/{doc.id}/reservations') \
                .document(str(record.get("id"))) \
                .set(resv_info, merge=True)
            logging.debug(f"added to {doc.id}")


class ReservationSync:

    def __init__(self, orgId: str, g_cloud_token=None):
        self.orgId = orgId
        self.mongo = Mongodb(orgId)
        self.mongoV2 = MongodbV2(orgId)
        self.token: Token = get_key(self.orgId)
        self.g_cloud_token = g_cloud_token
        self.__urgent_booking_criteria__ = 5 * 86400
        self.__stay_duration_criteria__ = 10 * 86400
        self.__booking_category_levels__ = ['bronze', 'silver', 'gold', 'platinum']

    def _get_booking_type(self, arrival_date: str, created_date: str):
        result = 'unknown'
        try:
            delta = datetime.fromisoformat(arrival_date) - datetime.fromisoformat(created_date)
            delta = delta.days * 86400 + delta.seconds
            result = 'Urgent Booking' if delta < self.__urgent_booking_criteria__ else 'Pre Planned'
        except Exception as e:
            logging.error('Error while calculating booking type')
            logging.error(e)
        finally:
            return result

    def _get_duration_type(self, departure_date: str, arrival_date: str):
        result = 'unknown'
        try:
            stay_d = datetime.fromisoformat(departure_date) - datetime.fromisoformat(arrival_date)
            delta = stay_d.days * 86400 + stay_d.seconds
            result = 'Short Stay' if delta < self.__stay_duration_criteria__ else 'Long Stay'
        except Exception as e:
            logging.error('Error calculating stay duration type')
            logging.error(e)
        finally:
            return result

    def _get_booking_level(self, orgId, clientId, departure_date: str, arrival_date: str, spend, booking_type):
        result = 'unknown'
        try:
            stay_d = datetime.fromisoformat(departure_date) - datetime.fromisoformat(arrival_date)
            booking_type_id = 1 if booking_type == 'Urgent Booking' else 0
            model = get_model_from_cloud_storage(
                str(orgId),
                f'booking_categorization_{clientId}.pkl',
                token=self.g_cloud_token
            )
            prediction = model.predict([[stay_d.days, spend, booking_type_id]])
            level = prediction[0] if len(prediction) > 0 else None
            result = self.__booking_category_levels__[level] if level else 'unknown'
        except Exception as e:
            logging.error('Error calculating booking_level of reservation')
            logging.error(e)
        finally:
            return result

    def _retrieve_data(self, id, name, url):
        result = None
        try:
            logging.debug(f'Extracting {name} for reservation: {id}')
            header = {
                'Content-Type': 'application/json',
                'authtoken': self.token.key
            }
            response = requests.request("GET", url, headers=header)
            if response.status_code == 200:
                result = response.json()
            else:
                logging.error(f'Error getting {name} for reservation {id} due to status code {response.status_code}')
                logging.error(url.format(id))
        except Exception as e:
            logging.error(f' {name} failed due to {e}')
        finally:
            return result

    def extract_reservation_details(self, record):
        feature_list = [
            {
                'name': 'holds',
                'url': 'holds'
            },
            {
                'name': 'guests',
                'url': 'guests'
            },
            {
                'name': 'billTo',
                'url': 'billTo'
            },
            {
                'name': 'transfers',
                'url': 'transfers'
            },
            {
                'name': 'auditTrail',
                'url': 'auditTrail'
            },
            {
                'name': 'daily_rates',
                'url': 'dailyRates'
            },
            {
                'name': 'rego_access',
                'url': 'regoAccess'
            },
            {
                'name': 'requirement',
                'url': 'requirements'
            },
            {
                'name': 'housekeeping',
                'url': 'housekeeping'
            },
            {
                'name': 'daily_revenue',
                'url': 'dailyRevenue'
            },
            {
                'name': 'add_ons',
                'url': 'reservationAddOn'
            },
            {
                'name': 'correspondence',
                'url': 'correspondence'
            },
            {
                'name': 'financial_info_actual',
                'url': 'actualAccount'
            },
            {
                'name': 'bedConfiguration',
                'url': 'bedConfiguration'
            },
            {
                'name': 'existingToken',
                'url': 'existingToken'
            },
            {
                'name': 'projectedAccount',
                'url': 'projectedAccount'
            }
        ]
        try:
            logging.debug(f"Extracting reservation {record.get('id')} additional details.")

            for item in feature_list:
                _url = f"{self.token.hostName}/reservations/{record.get('id')}/{item.get('url')}"
                record[item.get('name')] = self._retrieve_data(record.get("id"), item.get("name"), _url)

            _field = 'reservationTypes'
            _url = f"{self.token.hostName}/reservationTypes/{record.get('resTypeId')}"
            record[_field] = self._retrieve_data(record.get("id"), _field, _url)

            _field = 'marketSegment'
            _url = f"{self.token.hostName}/marketSegments/{record.get('marketSegmentId')}"
            record[_field] = self._retrieve_data(record.get("id"), _field, _url)

            _field = 'subMarketSegment'
            _url = f"{self.token.hostName}/marketSegments/{record.get('marketSegmentId')}/subMarketSegments"
            record[_field] = [item for item in self._retrieve_data(record.get("id"), _field, _url) if
                              item['id'] == record.get('subMarketSegmentId')]

            return record
        except Exception as e:
            logging.error(f'Error retrieving addition reservation details for {record.get("id")}')
            logging.error(e)

    def _extract_guest_profile(self, guest):
        guestId = 0
        try:
            guestId = guest.get('id')

            _field = 'accounts'
            _url = f"{self.token.hostName}/guests/{guestId}/accounts"
            guest[_field] = self._retrieve_data(guestId, _field, _url)

            _field = 'contracts'
            _url = f"{self.token.hostName}/guests/{guestId}/contracts"
            guest[_field] = self._retrieve_data(guestId, _field, _url)
        except Exception as e:
            logging.error(logging.error(f'Guest profile not found : {guestId}'))
            logging.error(e)
        finally:
            return guest

    def _get_guest_list(self, record):
        logging.debug(f'Processing guest list of size: {len(record.get("guests"))}')
        _guest_list = list()
        try:
            for guest in record.get('guests'):
                _guest_profile = _transform_guest_profile(self._extract_guest_profile(guest))
                self.mongoV2.save(_guest_profile)
                _guest_list.append(ReservationGuestShort(
                    guest=str(guest.get('id')),
                    primary=guest.get('id') == record.get("guestId"),
                    arrivalTransport=None,
                    departureTransport=None
                ))
        except Exception as e:
            logging.error('Error getting guest list')
            logging.error(e)
        return _guest_list

    def _get_guest_info(self, record):
        guest_info = ReservationGuestInfo(
            adults=record.get('adults'),
            children=record.get('children'),
            infants=record.get('infants'),
            childBuckets=None,
            preRegistered=None,  # TODO : create logic to see if user already existed or not
            guest_list=self._get_guest_list(record)
        )
        return guest_info

    def _get_transaction_info(self, resvId):
        result = None
        try:
            logging.debug(f'Extracting transactions for reservation: {resvId}')
            header = {
                'Content-Type': 'application/json',
                'authtoken': self.token.key
            }
            url = f"{self.token.hostName}/transactions/search?limit=500&offset=0"
            body = {
                'reservationIds': [
                    resvId
                ]
            }
            response = requests.request("POST", url, headers=header, data=json.dumps(body))
            if response.status_code == 200:
                result = response.json()
            else:
                logging.error(f'Error getting transactions for reservation {resvId} due to status code {response.status_code}')
                logging.error(url.format(resvId))
                logging.error(body)
        except Exception as e:
            logging.error(f' {resvId} failed due to {e}')
            logging.error(e)
        finally:
            return result

    def transform_reservation(self, record):
        try:
            logging.debug(f'Transforming reservation {record.get("id")}')
            reservationV2 = ReservationModelV2(
                _id=str(record.get('id')),
                orgId=self.orgId,
                idObj=_create_reservation_id_obj(record),
                agent=record.get('agent'),
                datesAndDuration={
                    'createdDate': record.get('createdDate'),
                    'confirmedDate': record.get('confirmedDate'),
                    'arrivalDate': record.get('arrivalDate'),
                    'departureDate': record.get('departureDate'),
                    'cancelledDate': record.get('cancelledDate'),
                    'expectedTimes': {
                        'arrival': record.get('arrivalDate'),
                        'departure': record.get('departureDate')
                    },
                    'originalTimeSpan': None,
                    'lastModifyDateTime': record.get('modifiedDate'),
                    'createBusinessDate': record.get('createdDate').split(' ')[0],
                    'createDateTime': record.get('createdDate'),
                    'eta': record.get('eta'),
                    'event': {
                        'eventName': record.get('eventName'),
                        'eventFinish': record.get('eventFinish'),
                        'eventStart': record.get('eventStart'),
                        'attendees': record.get('attendees'),
                    }
                },
                status=_get_status(record.get('status')),
                correspondence=record.get('correspondence'),
                metaInfo={
                    'allowAutoCheckin': None,
                    'allowMobileCheckout': True,
                    'allowMobileViewFolio': True,
                    'allowPreRegistration': True,
                    'allowedActions': True,
                    'computedReservationStatus': None,
                    'creatorId': record.get('createdById'),
                    'postStayChargeAllowed': False,
                    'preStayChargeAllowed': False,
                    'autoCheckInAllowed': False,
                    'postToNoShowCancelAllowed': False,
                    'stampDutyExists': None,
                    'roomAndTaxPosted': None,
                    'hasOpenFolio': None,
                    'lastModifierId': record.get('modifiedById'),
                    'optedForCommunication': True,
                    'walkIn': False,
                    'printRate': None,
                    'remoteCheckInAllowed': True,
                    'roomNumberLocked': True,
                    'holds': record.get('holds')
                },
                property={
                    'hotelId': str(record.get('clientId')),
                    'hotelName': record.get('propertyName'),
                    'roomId': record.get('areaId'),
                    'roomName': record.get('areaName'),
                    'categoryName': record.get('categoryName'),
                    'bedConfiguration': record.get('bedConfiguration')
                },
                stayInfo={
                    'longTerm': record.get('longTerm'),
                    'businessSegmentId': record.get('businessSegmentId'),
                },
                reservationTypes={
                    'id': record.get('reservationTypes').get('id') if record.get('reservationTypes') else None,
                    'name': record.get('reservationTypes').get('name') if record.get('reservationTypes') else None,
                    'type': record.get('reservationType'),
                    'inactive': record.get('reservationTypes').get('inactive') if record.get('reservationTypes') else None,
                    'fixedRes': record.get('fixedRes'),
                    'fixedResReasonId': record.get('fixedResReasonId'),
                },
                bookingInfo={
                    'upgradeEligible': False,  # TODO : write logic to check if booking is upgrade eligible
                    'upgradeReason': record.get('financial_info_actual').get('upgradeReason'),
                    # 'bookingMedium': record.get('roomStay'),
                    # 'bookingMediumDescription': record.get('roomStay'),
                    'sourceOfSaleType': record.get('bookingSourceName'),
                    'sourceOfSaleCode': record.get('bookingSourceId'),
                    'travelAgentId': record.get('travelAgentId'),
                    'travelAgentName': record.get('travelAgentName'),
                    'marketSegment': record.get('marketSegment'),
                    'subMarketSegment': record.get('subMarketSegment'),
                    'notes': record.get('notes'),
                    'otaNotes': record.get('otaNotes'),
                    'mealPlanId': record.get('mealPlanId'),
                    'otaRef1': record.get('otaRef1'),
                    'otaRef2': record.get('otaRef2'),
                    'otaRef3': record.get('otaRef3')
                },
                financeInfo={
                    'accountId': record.get('accountId'),
                    'rateTypeId': record.get('rateTypeId'),
                    'rateTypeName': record.get('rateTypeName'),
                    'rateOnGroup': record.get('rateOnGroup'),
                    'voucherId': record.get('voucherId'),
                    'billCategoryType': record.get('financial_info_actual').get('billCategoryType'),
                    'createTotalRate': record.get('financial_info_actual').get('createTotalRate'),
                    'preAuthCode': record.get('preAuthCode'),
                    'preAuthAmount': record.get('preAuthAmount'),
                    'preAuthExpDate': record.get('preAuthExpDate'),
                    'totalPoints': None,
                    'totalSpending': {
                        'amountBeforeTax': record.get('financial_info_actual').get('baseRate'),
                        'taxAmount': record.get('financial_info_actual').get('tax'),
                        'totalRate': record.get('financial_info_actual').get('totalRate')
                    },
                    'projectedTotalSpending': {
                        'amountBeforeTax': record.get('projectedAccount').get('balance'),
                        'taxAmount': record.get('projectedAccount').get('tax'),
                        'totalRate': record.get('projectedAccount').get('total')
                    },
                    'paymentMethod': {
                        'paymentModeId': record.get('paymentModeId')
                    },
                    'other': {
                        'arBalance': record.get('financial_info_actual').get('arBalance'),
                        'accommodationBalance': record.get('financial_info_actual').get('accommodationBalance'),
                        'electricityBalance': record.get('financial_info_actual').get('electricityBalance'),
                        'extrasBalance': record.get('financial_info_actual').get('extrasBalance'),
                        'gasBalance': record.get('financial_info_actual').get('gasBalance'),
                        'waterBalance': record.get('financial_info_actual').get('waterBalance'),
                        'phoneBalance': record.get('financial_info_actual').get('phoneBalance'),
                        'internetBalance': record.get('financial_info_actual').get('internetBalance'),
                    },
                    'revenueBucketsInfo': None,
                    'transactions': self._get_transaction_info(record.get('id')),
                    'revenue': {
                            'totalFixedCharge': {
                                'amount': record.get('financial_info_actual').get('baseRate')
                            },
                            'totalPayment': {
                                'amount': record.get('financial_info_actual').get('totalRate')
                            },
                            'roomRevenue': {
                                'amount': sum([item['accommodation'] for item in record.get('daily_revenue')])
                            },
                            'foodAndBevRevenue': {
                                'amount': sum([item['foodAndBeverage'] for item in record.get('daily_revenue')])
                            },
                            'otherRevenue': {
                                'amount': sum([item['other'] for item in record.get('daily_revenue')]),
                            },
                            'totalRevenue': {
                                'amount': sum([item['accommodation'] for item in record.get('daily_revenue')]) + sum(
                                    [item['foodAndBeverage'] for item in record.get('daily_revenue')]) + sum(
                                    [item['other'] for item in record.get('daily_revenue')])
                            },
                            'balance': {
                                'amount': record.get('financial_info_actual').get('accommodationBalance')
                            }
                        },
                    'deposit': {
                        'deposit': record.get('financial_info_actual').get('deposit'),
                        'depositRequiredByDate': record.get('financial_info_actual').get('depositRequiredByDate'),
                        'secondDeposit': record.get('financial_info_actual').get('secondDeposit'),
                        'secondDepositRequiredByDate': record.get('financial_info_actual').get('secondDepositRequiredByDate'),
                    },
                    'discount': [
                        {
                            'id': record.get('financial_info_actual').get('discountId'),
                            'name': record.get('financial_info_actual').get('discountName'),
                            'reason': record.get('financial_info_actual').get('discountReason'),
                            'amount': record.get('financial_info_actual').get('discountAmount')
                        }
                    ],
                    'package': [
                        {
                            'amount': record.get('financial_info_actual').get('package')
                        }
                    ],
                    'commission': {
                        'travelAgentCommissionPercentage': record.get('financial_info_actual').get('financial_info_actual')
                    },
                    'billTo': record.get('billTo'),
                    'billing': record.get('billing')
                },
                daily_activity=_generate_day_to_day_entry(record),
                linkedReservation=record.get('linkedReservation'),
                guestInfo=self._get_guest_info(record),
                eCertificates=[record.get('existingToken')],
                historyEvents=record.get('auditTrail'),
                cancellation=[
                    {
                        'reason': None,
                        'cxlDate': record.get('cancelledDate'),
                        'userId': record.get('cancelledById'),
                        'policy': record.get('cancellationPolicyId'),
                        'externalCancelId': record.get('externalCancelId'),
                        'businessLostId': record.get('businessLostId')
                    }
                ],
                housekeeping=record.get('housekeeping'),
                comments=record.get('comments'),
                policies=record.get('reservationPolicies'),
                inventoryItems=record.get('inventoryItems'),
                preferences=[],
                requirement=[],
                rego_access=record.get('rego_access'),
                memberships=None,
                packages=record.get('add_ons'),
                transfers=record.get('transfers'),
                auraRecordUpdatedOn=datetime.now()
            )
            return reservationV2
        except Exception as e:
            logging.error(f"Exception while transforming reservation {record.get('id')}")
            logging.error(e)

    def extract_reservation(self, record):
        reservationId = record.get("reservation")
        logging.info(f'Extracting reservation: {reservationId}')

        header = {
            'Content-Type': 'application/json',
            'authtoken': self.token.key
        }
        url = f"{self.token.hostName}/reservations/{reservationId}?modelType=full"
        response = requests.request("GET", url, headers=header)
        if response.status_code == 200:
            try:
                response_json = dict(response.json())
                response_json['orgId'] = self.orgId
                response_json['agent'] = record.get('agent')
                property_info = self.mongo.get_collection(self.mongo.PROPERTY_COLLECTION).find_one(
                    {"areas.id": response_json.get('areaId')},
                    {'id': 1, 'name': 1,
                     'clientId': 1}
                )
                response_json['clientId'] = property_info.get('clientId') if property_info else 0
                response_json['propertyId'] = property_info.get('_id') if property_info else 0
                response_json['propertyName'] = property_info.get('name') if property_info else 'Unknown'
                return response_json
            except Exception as err:
                logging.error(f'{record} load failed due to {err}')
        else:
            logging.error(f"RMS returned status code {response.status_code} "
                          f"for reservation {reservationId} ")
            raise Exception('Reservation not found / unable to retrieve')

    def process(self, reservationId):
        record = {
            'orgId': self.orgId,
            'agent': NAME,
            'reservation': reservationId
        }

        if not validate_key(self.token.validity):
            logging.debug('Refreshing RMS token as it is about to expire')
            self.token = get_key(self.orgId)

        record = self.extract_reservation(record)
        if record:
            record = self.extract_reservation_details(record)
            record = self.transform_reservation(record)
            self.mongoV2.save(record)
            # self._add_reservation_to_alvie(record)

    def __del__(self):
        if self.mongo:
            self.mongo.close_connection()
