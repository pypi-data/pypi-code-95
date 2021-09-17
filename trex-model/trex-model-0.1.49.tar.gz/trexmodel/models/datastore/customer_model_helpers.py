'''
Created on 29 Apr 2021

@author: jacklok
'''
from trexlib.utils.string_util import is_empty, is_not_empty
from datetime import datetime
import logging

logger = logging.getLogger('helper')


'''
Customer Reward Summary format is
{
    [reward_format] : {
                        'latest_expiry_date'     : [expiry date],
                        'amount'                 : [reward balance],
                        }

}

'''
''' --------------- Start: Update reward summary for point and stamp--------------'''
def update_reward_summary_with_new_reward(existing_reward_summary, new_reward_details):
    reward_format               = new_reward_details.get('reward_format')
    reward_amount               = new_reward_details.get('amount')
    used_reward_amount          = new_reward_details.get('used_amount')
    latest_expiry_date          = datetime.strptime(new_reward_details.get('expiry_date'), '%d-%m-%Y').date()
    
    
    existing_latest_expiry_date = None
    new_latest_expiry_date      = latest_expiry_date
    
    if is_empty(existing_reward_summary):
        existing_reward_summary = {
                            reward_format:{
                                            'latest_expiry_date'    : new_latest_expiry_date.strftime('%d-%m-%Y'),
                                            'amount'                : reward_amount - used_reward_amount
                                            }
                                        
                            }
    else:
        reward_summary_by_reward_format = existing_reward_summary.get(reward_format)
        
        if reward_summary_by_reward_format is None:
            reward_summary_by_reward_format = {
                                                'amount': 0,
                                                }
            new_latest_expiry_date = latest_expiry_date
        else:
        
            existing_latest_expiry_date = reward_summary_by_reward_format.get('latest_expiry_date')
            existing_latest_expiry_date = datetime.strptime(existing_latest_expiry_date, '%d-%m-%Y').date()
            new_latest_expiry_date      = latest_expiry_date
            
            if latest_expiry_date > existing_latest_expiry_date:  
                new_latest_expiry_date = existing_latest_expiry_date
                
                
        reward_summary_by_reward_format['latest_expiry_date']   = new_latest_expiry_date.strftime('%d-%m-%Y')
        reward_summary_by_reward_format['amount']               = reward_summary_by_reward_format['amount'] + (reward_amount - used_reward_amount)
        existing_reward_summary[reward_format]                  = reward_summary_by_reward_format
        
    return existing_reward_summary

def update_reward_summary_with_reverted_reward(existing_reward_summary, reverting_reward_details):
    reward_summary              = existing_reward_summary
    reward_format               = reverting_reward_details.get('reward_format')
    reward_amount               = reverting_reward_details.get('amount')
    
    logger.debug('update_reward_summary_with_reverted_reward: reward_format=%s', reward_format)
    logger.debug('update_reward_summary_with_reverted_reward: reward_amount=%s', reward_amount)
    
    existing_latest_expiry_date = None
    
    if is_not_empty(reward_summary):
        reward_summary_by_reward_format = reward_summary.get(reward_format)
        
        logger.debug('update_reward_summary_with_reverted_reward: reward_summary_by_reward_format=%s', reward_summary_by_reward_format)
        if reward_summary_by_reward_format:
            existing_latest_expiry_date = reward_summary_by_reward_format.get('latest_expiry_date')
            existing_latest_expiry_date = datetime.strptime(existing_latest_expiry_date, '%d-%m-%Y').date()
            
            final_reward_amount                         = reward_summary_by_reward_format['amount'] - reward_amount
            reward_summary_by_reward_format['amount']   = final_reward_amount
            reward_summary[reward_format]               = reward_summary_by_reward_format
            
            if final_reward_amount==0:
                del reward_summary[reward_format]
        
    return reward_summary

''' --------------- End: Update reward summary for point and stamp--------------'''

'''
customer entitled_voucher_summary format is
{
    voucher_key : 
                label : xxxxxx,
                image_url : xxxxxxxx,
                redeem_info_list :    [
                                        {
                                            redeem_code: xxxxxxxxxx,
                                            effective_date : xxxxxxxx,
                                            expiry_date : xxxxxxxx
                                        }
                                    ]

}

'''

''' --------------- Start: Update reward summary for voucher--------------'''
def update_customer_entiteld_voucher_summary_with_customer_new_voucher(customer_entitled_voucher_summary, customer_voucher):
    merchant_voucher        = customer_voucher.entitled_voucher_entity
    voucher_key             = merchant_voucher.key_in_str
    voucher_label           = merchant_voucher.label
    voucher_image_url       = merchant_voucher.image_public_url
    redeem_info_list        = [customer_voucher.to_redeem_info()]
    
    return update_customer_entiteld_voucher_summary_with_new_voucher_info(customer_entitled_voucher_summary, 
                                                                          voucher_key, 
                                                                          voucher_label, 
                                                                          voucher_image_url,
                                                                          redeem_info_list)

def update_customer_entiteld_voucher_summary_with_new_voucher_info(customer_entitled_voucher_summary, merchant_voucher_key, voucher_label, 
                                                              voucher_image_url, redeem_info_list):
    
    if customer_entitled_voucher_summary is None:
        customer_entitled_voucher_summary = {}
        
    voucher_summary     = customer_entitled_voucher_summary.get(merchant_voucher_key)
    
    if voucher_summary:
        customer_entitled_voucher_summary[merchant_voucher_key]['redeem_info_list'].extend(redeem_info_list)  
    else:
        voucher_summary = {
                            'label'             : voucher_label,
                            'image_url'         : voucher_image_url,
                            'redeem_info_list'  : redeem_info_list 
                            
                            }
        customer_entitled_voucher_summary[merchant_voucher_key] = voucher_summary

    return customer_entitled_voucher_summary

def update_customer_entiteld_voucher_summary_after_reverted_voucher(customer_entitled_voucher_summary, reverted_customer_voucher):
    '''
    removed entitled voucher from customer entitled voucher summary 
    '''
    if customer_entitled_voucher_summary:
        merchant_voucher_key                    = reverted_customer_voucher.entitled_voucher_key
        redeem_code_of_reverting_voucher        = reverted_customer_voucher.redeem_code
        
        voucher_summary = customer_entitled_voucher_summary.get(merchant_voucher_key)
        
        if voucher_summary:
            new_redeem_info_list = []
            
            for redeem_info in voucher_summary.get('redeem_info_list'):
                if redeem_info.get('redeem_code')!=redeem_code_of_reverting_voucher:
                    new_redeem_info_list.append(redeem_info)
                
            
            if len(new_redeem_info_list) ==0:
                del customer_entitled_voucher_summary[merchant_voucher_key]
            else:
                customer_entitled_voucher_summary[merchant_voucher_key] = new_redeem_info_list
    return customer_entitled_voucher_summary
    
    
def update_customer_entiteld_voucher_summary_after_redeemed_voucher(entitled_voucher_summary, redeemed_customer_voucher):
    return update_customer_entiteld_voucher_summary_after_reverted_voucher(entitled_voucher_summary, redeemed_customer_voucher)

''' --------------- End: Update reward summary for voucher--------------'''

''' --------------- Start: Update reward summary for prepaid--------------'''

def update_prepaid_summary_with_new_prepaid(existing_prepaid_summary, new_prepaid_summary):
    prepaid_amount              = new_prepaid_summary.get('amount')
    used_prepaid_amount         = new_prepaid_summary.get('used_amount')
    
    if is_empty(existing_prepaid_summary):
        prepaid_balance         = prepaid_amount - used_prepaid_amount
        existing_prepaid_summary = {
                                    'amount'  : prepaid_balance,
                                    }
        
    else:
        prepaid_balance = existing_prepaid_summary.get('amount') + (prepaid_amount-used_prepaid_amount)
        existing_prepaid_summary = {
                                    'amount'  : prepaid_balance,
                                    }        
                
    return existing_prepaid_summary

def update_prepaid_summary_with_reverted_prepaid(existing_prepaid_summary, reverted_prepaid_summary):
    prepaid_amount              = reverted_prepaid_summary.get('amount')
    used_prepaid_amount         = reverted_prepaid_summary.get('used_amount')
    
    if is_empty(existing_prepaid_summary):
        existing_prepaid_summary = {
                                    'amount'  : .0,
                                    }
        
    else:
        prepaid_balance = existing_prepaid_summary.get('amount') - (prepaid_amount-used_prepaid_amount)
        if prepaid_balance<0:
            prepaid_balance = .0
        
        existing_prepaid_summary = {
                                    'amount'  : prepaid_balance,
                                    }        
                
    return existing_prepaid_summary

''' --------------- End: Update reward summary for prepaid--------------'''