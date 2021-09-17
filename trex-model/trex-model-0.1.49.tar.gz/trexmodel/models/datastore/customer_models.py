'''
Created on 5 Jan 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty, is_empty
import logging
from trexlib.utils.common.cache_util import cache
from trexlib.utils.common.date_util import convert_date_to_datetime,\
    to_day_of_year
from trexmodel import conf
from six import string_types
from datetime import datetime, timedelta
from trexmodel.models.datastore.customer_model_helpers import update_reward_summary_with_new_reward
from trexmodel.models.datastore.membership_models import MerchantTierMembership

logger = logging.getLogger('model')


class Customer(BaseNModel, DictModel, FullTextSearchable):
    '''
    parent is User
    '''
    
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    outlet                      = ndb.KeyProperty(name="outlet", kind=Outlet)
    merchant_reference_code     = ndb.StringProperty(name="merchant_reference_code", required=False)
    registered_datetime         = ndb.DateTimeProperty(required=False, auto_now_add=True)
    modified_datetime           = ndb.DateTimeProperty(required=False, auto_now=True)
    
    #---------------------------------------------------------------------------
    # User denormalize fields
    #---------------------------------------------------------------------------
    name                        = ndb.StringProperty(required=False)
    mobile_phone                = ndb.StringProperty(required=False)
    email                       = ndb.StringProperty(required=False)
    
    birth_date                  = ndb.DateProperty(required=False, indexed=False)
    birth_date_date_str         = ndb.StringProperty(required=False) 
    birth_day_in_year           = ndb.IntegerProperty(required=False)
    gender                      = ndb.StringProperty(required=False)
    reference_code              = ndb.StringProperty(required=True)
    
    mobile_app_installed        = ndb.BooleanProperty(required=False, default=False)
    
    tags_list                   = ndb.StringProperty(repeated=True, write_empty_list=True)
    
    memberships_list            = ndb.StringProperty(repeated=True, write_empty_list=True)
    
    last_transact_datetime      = ndb.DateTimeProperty(required=False)
    previous_transact_datetime  = ndb.DateTimeProperty(required=False)
    
    last_redeemed_datetime      = ndb.DateTimeProperty(required=False)
    
    tier_membership             = ndb.KeyProperty(name="tier_membership", kind=MerchantTierMembership)
    previous_tier_membership    = ndb.KeyProperty(name="previous_tier_membership", kind=MerchantTierMembership)
    
    reward_summary                      = ndb.JsonProperty()
    prepaid_summary                     = ndb.JsonProperty()
    entitled_voucher_summary            = ndb.JsonProperty()
    entitled_birthday_reward_summary    = ndb.JsonProperty()
    
    kpi_summary                         = ndb.JsonProperty()
    
    fulltextsearch_field_name           = 'name'
    
    dict_properties     = ['name', 'mobile_phone', 'email', 'gender', 'birth_date', 'reference_code', 'merchant_reference_code',  
                           'tags_list', 'memberships_list', 'registered_merchant_acct', 
                           'reward_summary', 'entitled_voucher_summary', 'prepaid_summary', 'kpi_summary', 'entitled_birthday_reward_summary',
                           'registered_outlet_key', 'registered_merchant_acct_key', 'registered_datetime', 'modified_datetime']
    
    @property
    def registered_user_acct_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def registered_user_acct(self):
        return User.fetch(self.key.parent().urlsafe())
    
    @property
    def registered_merchant_acct(self):
        return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @property
    def registered_merchant_acct_key(self):
        if self.merchant_acct:
            return self.merchant_acct.urlsafe().decode("utf-8")
    
    @property
    def registered_outlet(self):
        if self.outlet:
            return Outlet.fetch(self.outlet.urlsafe())
    
    @property
    def registered_outlet_key(self):
        if self.outlet:
            return self.outlet.urlsafe().decode("utf-8")
    
    @property
    def tier_membership_key(self):
        if self.tier_membership:
            return self.tier_membership.urlsafe().decode("utf-8")
        
    @staticmethod    
    def update_KPI(customer_acct, tags_list=None, memberships_list=None, tier_membership_key=None):
        if isinstance(tags_list, string_types):
            if is_not_empty(tags_list):
                tags_list = tags_list.split(',')
            else:
                tags_list = []
                
        if isinstance(memberships_list, string_types):
            if is_not_empty(memberships_list):
                memberships_list = memberships_list.split(',')
            else:
                memberships_list = []
        
        tier_membership = None
        
        if tier_membership_key:
            tier_membership = MerchantTierMembership.fetch(tier_membership_key)        
        
        customer_acct.tags_list         = tags_list
        customer_acct.memberships_list  = memberships_list
        customer_acct.tier_membership   = tier_membership
        customer_acct.put()
    
    @classmethod
    def get_by_reference_code(cls, reference_code):
        return cls.query(cls.reference_code==reference_code).get()
    
    @classmethod
    def get_by_merchant_reference_code(cls, merchant_reference_code):
        return cls.query(cls.merchant_reference_code==merchant_reference_code).get()
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query(cls.email==email).get()
    
    @classmethod
    def get_by_mobile_phone(cls, mobile_phone):
        return cls.query(cls.mobile_phone==mobile_phone).get()
    
    @classmethod
    def create(cls, merchant_acct=None, outlet=None, name=None, email=None, mobile_phone=None, merchant_reference_code=None, gender=None, birth_date=None,
               password=None):
        
        created_user = User.create(name=name, email=email, mobile_phone=mobile_phone, gender=gender, birth_date=birth_date, 
                           password=password)
        
        created_user.put()
        
        created_customer = cls.create_from_user(merchant_acct, outlet, created_user)
        
        return created_customer
    
    @classmethod
    def update(cls, customer=None, outlet=None, **kwargs):
        if outlet:
            customer.outlet = outlet.create_ndb_key()
        
        logger.debug('**kwargs=%s', kwargs)
        
        mobile_phone    = kwargs.get('mobile_phone')
        
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")
        
        kwargs['mobile_phone'] = mobile_phone
        
        for key, value in kwargs.items():
            setattr(customer, key, value)
            
        user_acct = customer.registered_user_acct
        
        User.update(user_acct=user_acct, **kwargs)
        '''
        user_acct.name                   = customer.name
        user_acct.email                  = customer.email
        user_acct.mobile_phone           = customer.mobile_phone
        user_acct.birth_date             = customer.birth_date
        user_acct.birth_date_date_str    = customer.birth_date_date_str
        user_acct.gender                 = customer.gender
        
        user_acct.put()
        '''
        customer.put()
        
    @classmethod
    def create_from_user(cls, merchant_acct, outlet, user_acct, merchant_reference_code=None):
        
        created_customer = cls(parent=user_acct.create_ndb_key(), 
                               outlet                   = outlet.create_ndb_key(), 
                               name                     = user_acct.name, 
                               email                    = user_acct.email, 
                               mobile_phone             = user_acct.mobile_phone, 
                               gender                   = user_acct.gender, 
                               reference_code           = user_acct.reference_code, 
                               birth_date               = user_acct.birth_date, 
                               birth_date_date_str      = user_acct.birth_date_date_str, 
                               birth_day_in_year        = user_acct.birth_day_in_year,
                               merchant_reference_code  = merchant_reference_code,
                               merchant_acct            = merchant_acct.create_ndb_key()
                           )
        
        created_customer.put()
        
        return created_customer
    
    @classmethod
    def list_merchant_customer_by_date_of_birth(cls, merchant_acct, date_of_birth, offset=0, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False, keys_only=False):
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key(), cls.birth_date_date_str==date_of_birth))
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only)
    
    @classmethod
    def list_merchant_customer_by_date_of_birth_thru_date_range(cls, merchant_acct, date_range_start=None, date_range_end=None, offset=0, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False, keys_only=False):
        date_range_start_day_in_year    = to_day_of_year(date_range_start)
        date_range_end_day_in_year      = to_day_of_year(date_range_end)
        
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key(), cls.birth_day_in_year>=date_range_start_day_in_year, cls.birth_day_in_year<=date_range_end_day_in_year))
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only)
    
    @classmethod
    def count_merchant_customer_by_date_of_birth(cls, merchant_acct, date_of_birth, limit=conf.MAX_FETCH_RECORD):
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key(), cls.birth_date_date_str==date_of_birth))
        
        return cls.count_with_condition_query(query, limit=limit)
    
    @classmethod
    def list_merchant_customer(cls, merchant_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key()))
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @classmethod
    def list_by_user_account(cls, user_acct):
        return cls.query(ancestor=user_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @classmethod
    def count_merchant_customer(cls, merchant_acct):
        if merchant_acct:
            query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key()))
        else:
            query = cls.query()
        
        return cls.count_with_condition_query(query)
    
    @classmethod
    def search_merchant_customer(cls, merchant_acct, name=None, email=None, mobile_phone=None, 
                                 reference_code=None, merchant_reference_code=None, merchant_tagging=None,
                                 registered_date_start=None, registered_date_end=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key()))
        
        if is_not_empty(email):
            query = query.filter(cls.email==email)
            
        elif is_not_empty(mobile_phone):
            query = query.filter(cls.mobile_phone==mobile_phone)
            
        elif is_not_empty(reference_code):
            query = query.filter(cls.reference_code==reference_code)
            
        elif is_not_empty(merchant_reference_code):
            query = query.filter(cls.merchant_reference_code==merchant_reference_code)
                    
        elif is_not_empty(merchant_tagging):
            query = query.filter(cls.tags_list==merchant_tagging)
        
        elif is_not_empty(name):
            search_text_list = name.split(' ')
        
        elif is_not_empty(registered_date_start) or is_not_empty(registered_date_end):
            
            if is_not_empty(registered_date_start):
                registered_datetime_start = convert_date_to_datetime(registered_date_start)
                
                query = query.filter(cls.registered_datetime>=registered_datetime_start)
            
            if is_not_empty(registered_date_end):
                registered_datetime_end = convert_date_to_datetime(registered_date_end)
            
                query = query.filter(cls.registered_datetime<registered_datetime_end)
        
        total_count                         = cls.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = cls.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    def update_from_user_acct(self, user_acct):
        
        self.name                   = user_acct.name
        self.email                  = user_acct.email
        self.mobile_phone           = user_acct.mobile_phone
        self.birth_date             = user_acct.birth_date
        self.birth_date_date_str    = user_acct.birth_date_date_str
        self.birth_day_in_year      = user_acct.birth_day_in_year
        self.gender                 = user_acct.gender
        self.put()
    
    @staticmethod
    def count_by_last_transact_date(merchant_acct, last_transact_in_day=7):
        checking_date = datetime.now().date() - timedelta(days=last_transact_in_day)
        
        logger.debug('count_by_last_transact_date: checking_date=%s', checking_date)
        
        query = Customer.query(ndb.AND(
                                                    Customer.merchant_acct==merchant_acct.create_ndb_key(),
                                                    Customer.last_transact_date >= checking_date   
                                        ))
        
        return Customer.count_with_condition_query(query)
    
    @staticmethod
    def update_customer_entitled_birthday_reward_summary(customer_acct, merchant_program_key, transact_datetime=None):
        
        logger.debug('---update_customer_entitled_birthday_reward_summary---')
        
        if transact_datetime is None:
            today       = datetime.today().date()
            this_year   = today.year
        else:
            today       = transact_datetime.date()
            this_year   = transact_datetime.year
        
        year_str = str(this_year)
        entitled_birthday_reward_summary            = customer_acct.entitled_birthday_reward_summary
        this_year_entitled_birthday_reward_summary  = None    
        
        if entitled_birthday_reward_summary:
            this_year_entitled_birthday_reward_summary  = entitled_birthday_reward_summary.get(year_str)
        else:
            entitled_birthday_reward_summary = {}
        
        if this_year_entitled_birthday_reward_summary is None:
            this_year_entitled_birthday_reward_summary = {}
            
        
        is_birthday_reward_has_been_given = False
        if this_year_entitled_birthday_reward_summary.get('programs'):
            if merchant_program_key in this_year_entitled_birthday_reward_summary.get('programs'):
                is_birthday_reward_has_been_given = True
                logger.debug('Found %s in programs list', merchant_program_key)
            else:
                logger.debug('going to add entitled program(%s)', merchant_program_key)
                this_year_entitled_birthday_reward_summary['programs'].append(merchant_program_key)
                is_birthday_reward_has_been_given = False
                
        else:
            this_year_entitled_birthday_reward_summary = {'programs': [merchant_program_key]}
            is_birthday_reward_has_been_given = False
            
        if is_birthday_reward_has_been_given==False:
            entitled_birthday_reward_summary[year_str]     = this_year_entitled_birthday_reward_summary
            customer_acct.entitled_birthday_reward_summary  = entitled_birthday_reward_summary
            customer_acct.put()
                
    
    @staticmethod
    def check_birthday_reward_have_entitled_before(customer_acct, year, program_key):
        entitled_birthday_reward_summary = customer_acct.entitled_birthday_reward_summary
        year_str = str(year)
        logger.info('entitled_birthday_reward_summary=%s', entitled_birthday_reward_summary)
        
        if is_not_empty(entitled_birthday_reward_summary):
            if is_not_empty(entitled_birthday_reward_summary.get(year_str)):
                this_year_entitled_birthday_programs_list = entitled_birthday_reward_summary.get(year_str).get('programs')
                
                logger.debug('this_year_entitled_birthday_programs_list=%s', this_year_entitled_birthday_programs_list)
                is_entitled_before = False
                if is_not_empty(this_year_entitled_birthday_programs_list):
                    for k in this_year_entitled_birthday_programs_list:
                        if k == program_key:
                            is_entitled_before =  True
                            break
                    
                    logger.debug('is_entitled_before=%s', is_entitled_before)
                    return is_entitled_before
                else:
                    logger.debug('Program list is empty')
            else:
                logger.debug('Not found for year (%s)', year)
        else:
            logger.debug('entitled_birthday_reward_summary is empty')            
        
        return False
    