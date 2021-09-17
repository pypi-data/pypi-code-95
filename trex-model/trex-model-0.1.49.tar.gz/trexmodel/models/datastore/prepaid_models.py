'''
Created on 24 Aug 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet, MerchantUser
import logging, json
from trexmodel import conf, program_conf
from trexlib.utils.string_util import random_string
from datetime import datetime, timedelta
import trexmodel.conf as model_conf
from trexlib.utils.common.common_util import sort_dict_list
from trexmodel.utils.model.model_util import generate_transaction_id

logger = logging.getLogger('model')

class PrepaidSettings(BaseNModel,DictModel):
    '''
    Merchant acct as ancestor
    '''
    label                               = ndb.StringProperty(required=True)
    
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    
    enabled                             = ndb.BooleanProperty(required=True, default=True)
    
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    
    is_multi_tier_prepaid               = ndb.BooleanProperty(default=False)
    is_lump_sum_prepaid                 = ndb.BooleanProperty(default=True)
    
    lump_sum_settings                   = ndb.JsonProperty(required=False)
    multitier_settings                  = ndb.JsonProperty(required=False)
    
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    dict_properties = ["label", "start_date", "end_date", "enabled", "created_datetime", "modified_datetime", "enabled",
                       "is_multi_tier_prepaid","is_lump_sum_prepaid", "lump_sum_settings", "multitier_settings", "multitier_settings_list"]
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def multitier_settings_list(self):
        multitier_settings = self.multitier_settings
        return_list = []
        for v in multitier_settings.values():
            return_list.append(v)
        return return_list
    
    @property
    def is_expiration_date_type(self):
        return self.expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE
    
    def to_configuration(self):
        prepaid_program_configuration =  {
                                                'program_key'   : self.key_in_str,
                                                'label'         : self.label,
                                                }
        if self.is_lump_sum_prepaid:
            prepaid_program_configuration['lump_sum_settings'] = self.lump_sum_settings
        
        if self.is_multi_tier_prepaid:
            prepaid_program_configuration['multitier_settings'] = self.multitier_settings
        
        return prepaid_program_configuration
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return PrepaidSettings.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    def __update_merchant_account_prepaid_configuration(self):
        merchant_acct = self.merchant_acct_entity    
        merchant_acct.update_prepaid_program(self.to_configuration())
        merchant_acct.put()
    
    @staticmethod
    def create(merchant_acct, label, start_date, end_date, is_multi_tier_prepaid=False, is_lump_sum_prepaid=True, lump_sum_settings=None, multitier_settings=None, created_by=None):
        prepaid_settings = PrepaidSettings(
                                parent                  = merchant_acct.create_ndb_key(),
                                label                   = label,
                                start_date              = start_date,
                                end_date                = end_date,
                                is_multi_tier_prepaid   = is_multi_tier_prepaid,
                                is_lump_sum_prepaid     = is_lump_sum_prepaid,
                                
                                lump_sum_settings       = lump_sum_settings,
                                multitier_settings      = multitier_settings,
                                
                                created_by              = created_by.create_ndb_key(),
                                created_by_username     = created_by.username,
                                )
        
        prepaid_settings.put()
        
        if prepaid_settings.enable:
            prepaid_settings.__update_merchant_account_prepaid_configuration()
        
    @staticmethod
    def update(prepaid_settings, label, start_date, end_date, is_multi_tier_prepaid=False, is_lump_sum_prepaid=True, lump_sum_settings=None, multitier_settings=None, modified_by=None):
        
        prepaid_settings.label                  = label
        prepaid_settings.start_date             = start_date
        prepaid_settings.end_date               = end_date
        prepaid_settings.is_multi_tier_prepaid  = is_multi_tier_prepaid
        prepaid_settings.is_lump_sum_prepaid    = is_lump_sum_prepaid
        prepaid_settings.lump_sum_settings      = lump_sum_settings
        prepaid_settings.multitier_settings     = multitier_settings
        prepaid_settings.modified_by            = modified_by.create_ndb_key()
        prepaid_settings.modified_by_username   = modified_by.username
        prepaid_settings.put()    
    
        if prepaid_settings.enable:
            prepaid_settings.__update_merchant_account_prepaid_configuration()
    
    
        return prepaid_settings
    
    @staticmethod
    def enable(prepaid_settings):
        prepaid_settings.enabled = True
        prepaid_settings.put()
        
        prepaid_settings.__update_merchant_account_prepaid_configuration()
        
    @staticmethod
    def disable(prepaid_settings):
        prepaid_settings.enabled = False
        prepaid_settings.put() 
        
        merchant_acct = prepaid_settings.merchant_acct_entity    
        merchant_acct.remove_prepaid_program_configuration(prepaid_settings.key_in_str)
        merchant_acct.put()

class CustomerPrepaidReward(BaseNModel,DictModel):
    '''
    Customer acct as ancestor
    '''
    merchant_acct                       = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    topup_outlet                        = ndb.KeyProperty(name="topup_outlet", kind=Outlet)
    
    topup_amount                        = ndb.FloatProperty(required=True, default=.0)
    topup_unit                          = ndb.IntegerProperty(required=True, default=.1)
    topup_prepaid_rate                  = ndb.FloatProperty(required=True, default=.0)
    prepaid_amount                      = ndb.FloatProperty(required=True, default=.0)
    
    used_prepaid_amount                 = ndb.FloatProperty(required=False, default=.0)
    
    status                              = ndb.StringProperty(required=False, default=program_conf.REWARD_STATUS_VALID)
    
    transaction_id                      = ndb.StringProperty(required=True)
    invoice_id                          = ndb.StringProperty(required=False)
    
    #store prepaid program key, topup_amount, prepaid_amount scheme
    prepaid_scheme_details              = ndb.JsonProperty(required=False)
    
    topup_datetime                      = ndb.DateTimeProperty(required=True, auto_now_add=True)
    topup_by                            = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    
    reverted_datetime                   = ndb.DateTimeProperty(required=False)
    reverted_by                         = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username                = ndb.StringProperty(required=False)
    
    @property
    def is_valid(self):
        return self.status == program_conf.REWARD_STATUS_VALID
    
    @property
    def is_redeemed(self):
        return self.status == program_conf.REWARD_STATUS_REDEEMED
    
    @property
    def prepaid_balance(self):
        return self.prepaid_amount - self.used_prepaid_amount
    
    def update_used_reward_amount(self, used_prepaid_amount):
        self.used_prepaid_amount    += used_prepaid_amount
        prepaid_balance              = self.prepaid_balance
        
        logger.debug('CustomerCountableReward: prepaid_balance=%s', prepaid_balance)
        
        if prepaid_balance ==0:
            self.status = program_conf.REWARD_STATUS_REDEEMED
        
        self.put()
    
    @staticmethod
    def __calculate_topup_unit(topup_amount, prepaid_scheme_details):
        return int(topup_amount/prepaid_scheme_details.get('topup_amount'))
    
    @staticmethod
    def __calculate_prepaid_amount(topup_unit, prepaid_scheme_details):
        return topup_unit * prepaid_scheme_details.get('prepaid_amount')
    
    @staticmethod
    def __calculate_topup_prepaid_rate(prepaid_scheme_details):
        return float(prepaid_scheme_details.get('topup_amount')/prepaid_scheme_details.get('prepaid_amount'))
    
    def to_prepaid_summary(self):
        prepaid_summary =  {
                            'amount'            : self.prepaid_amount,
                            'used_amount'       : self.used_prepaid_amount,    
                            }
        
        return prepaid_summary
    
    @staticmethod
    def list_by_customer(customer, status=program_conf.REWARD_STATUS_VALID, limit = conf.MAX_FETCH_RECORD):
        return CustomerPrepaidReward.query(ndb.AND(CustomerPrepaidReward.status==status), ancestor=customer.create_ndb_key()).fetch(limit=limit)
    
    @staticmethod
    def list_all_by_customer(customer, limit = conf.MAX_FETCH_RECORD):
        return CustomerPrepaidReward.query(ancestor=customer.create_ndb_key()).fetch(limit=limit)
    
    @staticmethod
    def list_by_transaction_id(transaction_id):
        return CustomerPrepaidReward.query(CustomerPrepaidReward.transaction_id==transaction_id).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_by_customer_acct(customer_acct):
        return CustomerPrepaidReward.query(ndb.AND(CustomerPrepaidReward.status==program_conf.REDEEM_STATUS_VALID),ancestor=customer_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        
    @staticmethod
    def topup(customer_acct, topup_amount, prepaid_program, invoice_id=None, topup_outlet=None, topup_by=None, transaction_id=None):
        
        is_lump_sum_prepaid     = prepaid_program.is_lump_sum_prepaid
        is_multi_tier_prepaid   = prepaid_program.is_multi_tier_prepaid
        
        sorted_tier_scheme      = None
        
        prepaid_scheme_details  = {
                                    'program_key'   : prepaid_program.key_in_str
                                    }
        
        prepaid_scheme      = None
        
        if is_multi_tier_prepaid:
            sorted_tier_scheme = sort_dict_list(prepaid_program.multitier_settings.values(), 'min_topup_amount')
            
            logger.debug('Get topup scheme from topup amount(%s)', topup_amount)
            
            for scheme in sorted_tier_scheme:
                if topup_amount>= scheme.get('min_topup_amount'):
                    prepaid_scheme = {
                                            'topup_amount'  : scheme.get('topup_amount'),
                                            'prepaid_amount': scheme.get('prepaid_amount'),
                                            'prepaid_rate'  : scheme.get('prepaid_amount')/scheme.get('topup_amount'),
                                            'scheme_type'   : 'tier',
                                            }
                    logger.debug('Found topup scheme for min topup amount(%s)', scheme.get('min_topup_amount'))
        
        logger.debug('prepaid_scheme=%s', prepaid_scheme)
        
        #if topup amount is less than smallest prepaid tier minimum topup amount, thus goto lump sum scheme    
        if prepaid_scheme is None and is_lump_sum_prepaid:
            found_match_scheme = {
                                            'topup_amount'  : scheme.get('topup_amount'),
                                            'prepaid_amount': scheme.get('prepaid_amount'),
                                            'prepaid_rate'  : scheme.get('prepaid_amount')/scheme.get('topup_amount'),
                                            'scheme_type'   : 'lump_sum',
                                            }  
        
        if prepaid_scheme is None:
            prepaid_scheme = {
                                            'topup_amount'  : 1,
                                            'prepaid_amount': 1,
                                            'prepaid_rate'  : 1,
                                            'scheme_type'   : 'auto',
                                            }
            
            logger.debug('create default prepaid_scheme=%s', prepaid_scheme)
        
        prepaid_scheme_details.update(prepaid_scheme)
        
        logger.debug('prepaid_scheme_details=%s', prepaid_scheme_details)
            
        topup_unit          = CustomerPrepaidReward.__calculate_topup_unit(topup_amount, prepaid_scheme_details)
        prepaid_amount      = CustomerPrepaidReward.__calculate_prepaid_amount(topup_unit, prepaid_scheme_details)
        topup_prepaid_rate  = CustomerPrepaidReward.__calculate_topup_prepaid_rate(prepaid_scheme_details)
        
        topup_by_key = None
        
        if topup_by:
            topup_by_key = topup_by.create_ndb_key()
            
        merchant_acct               = customer_acct.registered_merchant_acct
        prepaid_topup_reward        = CustomerPrepaidReward(
                                                            parent                  = customer_acct.create_ndb_key(),
                                                            merchant_acct           = merchant_acct.create_ndb_key(),
                                                            topup_outlet            = topup_outlet.create_ndb_key(),
                                                            topup_amount            = topup_amount,
                                                            topup_unit              = topup_unit,
                                                            prepaid_amount          = prepaid_amount,
                                                            topup_prepaid_rate      = topup_prepaid_rate,
                                                            used_prepaid_amount     = .0,
                                                            prepaid_scheme_details  = prepaid_scheme_details,
                                                            
                                                            transaction_id          = transaction_id,
                                                            invoice_id              = invoice_id,
                                                            
                                                            topup_by                = topup_by_key,
                                                            )
        
        prepaid_topup_reward.put()
        
        return prepaid_topup_reward
    
    
