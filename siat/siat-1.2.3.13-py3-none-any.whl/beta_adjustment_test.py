# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os; os.chdir("S:/siat")
from siat.beta_adjustment import *

yearlist=gen_yearlist('2011','2020')
betas=betas_dji=get_beta_ML('EDU','^DJI',yearlist)

betas_dji=get_beta_ML('IDCBY','^DJI',yearlist)

betas_sp500=get_beta_ML('IDCBY','^GSPC',yearlist)

betas_sw=get_beta_SW('PG','^DJI', yearlist)

betas_sw_4452t=get_beta_SW('4452.T','^N225', yearlist)

yearlist=gen_yearlist('2011','2019')
betas_sw_hmif=get_beta_SW('HMI.F','^FCHI',yearlist)
betas_sw_diof=get_beta_SW('DIO.F','^FCHI', yearlist)

betas_dimson=get_beta_dimson('600376.SS','000001.SS', yearlist)
betas_dimson=get_beta_dimson('600340.SS','000001.SS', yearlist)

betas_hamada=get_beta_hamada2('600519.SS','000001.SS')

betas_hamada=get_beta_hamada2('600606.SS','000001.SS')

betas_hamada=get_beta_hamada2('GS','^GSPC')

#==============================================================================
stkcd='0700.HK'
mktidx='^HSI'
h=get_beta_hamada2(stkcd,mktidx)


from siat.financial_statements import *
fs_is=get_income_statements(stkcd).T
fs_bs=get_balance_sheet(stkcd).T

betas_hamada=get_beta_hamada_ts('600519.SS','000001.SS', yearlist)
import tushare as ts

pro=init_ts() 
is0=pro.income(ts_code='600519.SH')

token='49f134b05e668d288be43264639ac77821ab9938ff40d6013c0ed24f'
pro=ts.pro_api(token)
pro.income(ts_code='600519.sh')

R=prepare_capm(stkcd,mktidx,start,end)


betas1=get_beta_hamada2('0700.HK','^HSI')
betas1=get_beta_hamada2('MSFT','^GSPC')

betas1=get_beta_hamada2('BA','^GSPC')
betas1=get_beta_hamada2('GS','^GSPC')
betas1=get_beta_hamada2('AAPL','^GSPC')

betas1=get_beta_hamada2('000002.SZ','000001.SS')
betas1=get_beta_hamada2('600519.SS','000001.SS')
betas1=get_beta_hamada2('600606.SS','000001.SS')
#==============================================================================