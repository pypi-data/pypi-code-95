import logging
import json
import pickle
import os
import pandas as pd
import pyresdev.utils._regex_utils as reutils
import numpy as np

__all__ = ['create_address_pivot','clean_brackets_from_list','clean_brackets_from_string','extract_info_from_summaries']

def create_address_pivot(df):

    aux=pd.json_normalize(df[['linkedin_username','emails']].to_dict(orient='records'),record_path='emails',meta=['linkedin_username'])
    aux['type'].fillna('unknown',inplace=True)
    aux_pivot=aux.pivot_table(index=['linkedin_username'],columns=['type'],values=['address'],aggfunc= lambda x: ', '.join(map(str,x)))
    aux_pivot.columns= ['_'.join(col).strip() for col in aux_pivot.columns.values]
    aux_pivot.reset_index(inplace=True)
    return aux_pivot

def clean_brackets_from_list(df,column):
    df.loc[~df[column].isnull(),column]= df.loc[~df[column].isnull(),column].apply(lambda x: ','.join(map(str, x)))
    return df

def clean_brackets_from_string(df,column):
    df.loc[~df[column].isnull(),column] =  df.loc[~df[column].isnull(),column].apply(lambda x: x.replace('[','').replace(']',''))
    return df

def extract_info_from_summaries(df,column,is_list):
    #Convert experience list of dicts into a single string
    column_str=column+'_str'

    if is_list:
        print('column is list! converting to string')
        df[column_str]= df[column].apply(lambda x: ','.join(map(str,x)))
        df[column_str]=df[column_str].astype(str)
    else:
        print('column is not list! converting to string')
        df[column_str]=df[column].astype(str)
    
    # Phone numbers
    out_phone_column='out_phone_in_'+column
    mobile_phone_column='mobile_phone_in_'+column
    office_phone_column='office_phone_in_'+column
    df[out_phone_column],df[mobile_phone_column],df[office_phone_column] = zip(*df[column_str].apply(lambda x: reutils.search_for_phones(str(x))))
    print(f'{column} with phone numbers:')
    print(sum(df[out_phone_column].apply(lambda d: len(d))>0))
    for row in df[out_phone_column]:
        if '1-10' in row:
            row.remove('1-10')
        if '11-50' in row:
            row.remove('11-50')
        if '201-500' in row:
            row.remove('201-500')
        if '1001-5000' in row:
            row.remove('1001-5000')
        if '5001-10000' in row:
            row.remove('5001-10000')
        if '501-1000' in row:
            row.remove('501-1000')
        if '51-200' in row:
            row.remove('51-200')
    print(f'{column} with phone numbers after removing sizes:')
    print(sum(df[out_phone_column].apply(lambda d: len(d))>0))
    df[out_phone_column] = df[out_phone_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[out_phone_column].map(lambda d: len(d)) == 0,out_phone_column]=None
    df.loc[~df[out_phone_column].isnull(),out_phone_column]= df.loc[~df[out_phone_column].isnull(),out_phone_column].apply(lambda x: ','.join(map(str, x)))
    print(f'{column} with mobile phone numbers:')
    print(sum(df[mobile_phone_column].apply(lambda d: len(d))>0))
    df[mobile_phone_column] = df[mobile_phone_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[mobile_phone_column].map(lambda d: len(d)) == 0,mobile_phone_column]=None
    df.loc[~df[mobile_phone_column].isnull(),mobile_phone_column]= df.loc[~df[mobile_phone_column].isnull(),mobile_phone_column].apply(lambda x: ','.join(map(str, x)))
    print(f'{column} with office phone numbers:')
    print(sum(df[office_phone_column].apply(lambda d: len(d))>0))
    df[office_phone_column] = df[office_phone_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[office_phone_column].map(lambda d: len(d)) == 0,office_phone_column]=None
    df.loc[~df[mobile_phone_column].isnull(),mobile_phone_column]= df.loc[~df[mobile_phone_column].isnull(),mobile_phone_column].apply(lambda x: ','.join(map(str, x)))
    
    
    # emails
    mails_column='emails_found_in_'+column
    df[mails_column]= df[column_str].apply(lambda x: reutils.search_for_emails(str(x)))
    print(f'{column} with emails:')
    print(sum(df[mails_column].apply(lambda d: len(d))>0))
    df[mails_column] = df[mails_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[mails_column].map(lambda d: len(d)) == 0,mails_column]=None
    df.loc[~df[mails_column].isnull(),mails_column]= df.loc[~df[mails_column].isnull(),mails_column].apply(lambda x: ','.join(map(str, x)))
    
    # search_for_websites
    websites_column='websites_found_in_'+column
    df[websites_column]= df[column_str].apply(lambda x: reutils.search_for_websites(str(x)))
    print(f'{column} with websites:')
    df[websites_column] = df[websites_column].map(lambda l: list(map(str.strip, l)))
    print(sum(df[websites_column].apply(lambda d: len(d))>0))
    df.loc[df[websites_column].map(lambda d: len(d)) == 0,websites_column]=None
    df.loc[~df[websites_column].isnull(),websites_column]= df.loc[~df[websites_column].isnull(),websites_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_twitter_usernames
    twitter_column='twitter_found_in_'+column
    df[twitter_column]= df[column_str].apply(lambda x: reutils.search_for_twitter_usernames(str(x)))
    print(f'{column} with twitter:')
    print(sum(df[twitter_column].apply(lambda d: len(d))>0))
    df[twitter_column] = df[twitter_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[twitter_column].map(lambda d: len(d)) == 0,twitter_column]=None
    df.loc[~df[twitter_column].isnull(),twitter_column]= df.loc[~df[twitter_column].isnull(),twitter_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_facebook_profiles
    facebook_column='facebook_found_in_'+column
    df[facebook_column]= df[column_str].apply(lambda x: reutils.search_for_facebook_profiles(str(x)))
    print(f'{column} with facebook:')
    print(sum(df[facebook_column].apply(lambda d: len(d))>0))
    df[facebook_column] = df[facebook_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[facebook_column].map(lambda d: len(d)) == 0,facebook_column]=None
    df.loc[~df[facebook_column].isnull(),facebook_column]= df.loc[~df[facebook_column].isnull(),facebook_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_github_usernames
    github_column='github_found_in_'+column
    df[github_column]= df[column_str].apply(lambda x: reutils.search_for_github_usernames(str(x)))
    print(f'{column} with github:')
    print(sum(df[github_column].apply(lambda d: len(d))>0))
    df[github_column] = df[github_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[github_column].map(lambda d: len(d)) == 0,github_column]=None
    df.loc[~df[github_column].isnull(),github_column]= df.loc[~df[github_column].isnull(),github_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_instagram_profiles
    instagram_column='instagram_found_in_'+column
    df[instagram_column]=np.nan
    # df[instagram_column]= df[column_str].apply(lambda x: reutils.search_for_instagram_profiles(str(x)))
    # print(f'{column} with iinstagram:')
    # print(sum(df[instagram_column].apply(lambda d: len(d))>0))
    # df[instagram_column] = df[instagram_column].map(lambda l: list(map(str.strip, l)))
    # df.loc[df[instagram_column].map(lambda d: len(d)) == 0,instagram_column]=None
    # df.loc[~df[instagram_column].isnull(),instagram_column]= df.loc[~df[instagram_column].isnull(),instagram_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_linkedin_profiles
    linkedin_column='linkedin_found_in_'+column
    df[linkedin_column]=np.nan
    # df[linkedin_column]= df[column_str].apply(lambda x: reutils.search_for_linkedin_profiles(str(x)))
    # print(f'{column} with linkedin:')
    # print(sum(df[linkedin_column].apply(lambda d: len(d))>0))
    # df[linkedin_column] = df[linkedin_column].map(lambda l: list(map(str.strip, l)))
    # df.loc[df[linkedin_column].map(lambda d: len(d)) == 0,linkedin_column]=None
    # df.loc[~df[linkedin_column].isnull(),linkedin_column]= df.loc[~df[linkedin_column].isnull(),linkedin_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_linkedin_company
    linkedin_company_column='linkedin_company_found_in_'+column
    df[linkedin_company_column]= df[column_str].apply(lambda x: reutils.search_for_linkedin_company(str(x)))
    print(f'{column} with linkedin company:')
    print(sum(df[linkedin_company_column].apply(lambda d: len(d))>0))
    df[linkedin_company_column] = df[linkedin_company_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[linkedin_company_column].map(lambda d: len(d)) == 0,linkedin_company_column]=None
    df.loc[~df[linkedin_company_column].isnull(),linkedin_company_column]= df.loc[~df[linkedin_company_column].isnull(),linkedin_company_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_medium_user
    medium_column='medium_found_in_'+column
    df[medium_column] = np.nan
    # df[medium_column]= df[column_str].apply(lambda x: reutils.search_for_medium_user(str(x)))
    # print(f'{column} with medium:')
    # print(sum(df[medium_column].apply(lambda d: len(d))>0))
    # df[medium_column] = df[medium_column].map(lambda l: list(map(str.strip, l)))
    # df.loc[df[medium_column].map(lambda d: len(d)) == 0,medium_column]=None
    # df.loc[~df[medium_column].isnull(),medium_column]= df.loc[~df[medium_column].isnull(),medium_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_skype
    skype_column='skype_found_in_'+column
    df[skype_column]= df[column_str].apply(lambda x: reutils.search_for_skype(str(x)))
    print(f'{column} with skype:')
    print(sum(df[skype_column].apply(lambda d: len(d))>0))
    df[skype_column] = df[skype_column].map(lambda l: list(map(str.strip, l)))
    df.loc[df[skype_column].map(lambda d: len(d)) == 0,skype_column]=None
    df.loc[~df[skype_column].isnull(),skype_column]= df.loc[~df[skype_column].isnull(),skype_column].apply(lambda x: ','.join(map(str, x)))
    
    # reutils.search_for_telegram
    telegram_column='telegram_found_in_'+column
    df[telegram_column]=np.nan
    # df[telegram_column]= df[column_str].apply(lambda x: reutils.search_for_telegram(str(x)))
    # print(f'{column} with telegram:')
    # print(sum(df[telegram_column].apply(lambda d: len(d))>0))
    # df[telegram_column] = df[telegram_column].map(lambda l: list(map(str.strip, l)))
    # df.loc[df[telegram_column].map(lambda d: len(d)) == 0,telegram_column]=None

    return df


