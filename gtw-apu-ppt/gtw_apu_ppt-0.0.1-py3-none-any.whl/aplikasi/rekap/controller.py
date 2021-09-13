# from datetime import datetime
from datetime import *
import logging
import numpy as np
import pandas as pd
from pymysql import NULL
from sqlalchemy import create_engine
from flask import current_app as app
from aplikasi.utils import *

def data_member_gdc():
    sql = f"SELECT tgl_registrasi, kd_member, nama, syarat, notelp1, st_member FROM member"
    res = pd.read_sql(sql=sql, con=get_db_member_gdc())
    return res

def data_member_gdc_kd_member(kode_member= None):
    sql = f"SELECT * FROM member WHERE kd_member = '{kode_member}'"
    res = pd.read_sql(sql=sql, con=get_db_member_gdc())
    return res.to_dict(orient='records')

def data_member_gdc_disabled():
    sql = f"SELECT * FROM member_disabled"
    res = pd.read_sql(sql=sql, con=get_db_member_gdc())
    return res.to_dict(orient='records')

def data_member_gdc_disabled_kd_member(kode_member= None):
    sql = f"SELECT * FROM member_disabled WHERE kd_member='{kode_member}'"
    res = pd.read_sql(sql=sql, con=get_db_member_gdc())
    return res.to_dict(orient='records')

def data_riwayat_transaksi():
    sql = f"SELECT kd_member, no_telp_member, nama_member, gdc_id, jenis_trx, status_trx, \
    metode_bayar, tgl_trx, rp_trx, rp_biaya, rp_cashback, rp_bayar, desc_trx, cadangan1, \
    status_monitoring FROM db_gdcpay.riwayat_transaksi"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res

def data_riwayat_transaksi_kd_member(kode_member= None, gdc_id= None):
    sql = f"SELECT * FROM db_gdcpay.riwayat_transaksi WHERE kd_member= '{kode_member}' OR gdc_id= '{gdc_id}'"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_saldo():
    sql = f"SELECT * FROM db_gdcpay.saldo"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_saldo_kd_member(kode_member= None):
    sql = f"SELECT * FROM db_gdcpay.saldo WHERE kd_member= '{kode_member}'" 
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_saldo_blokir():
    sql = f"SELECT * FROM db_gdcpay.saldo_blokir"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_saldo_blokir_kd_member(kode_member= None, gdc_id= None):
    sql = f"SELECT * FROM db_gdcpay.saldo_blokir WHERE kd_member= '{kode_member}' OR gdc_id= '{gdc_id}'"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_tarik_dana_auth():
    sql = f"SELECT kd_member, nama_member, telp_member, rp_tarik, rp_biaya, \
    tgl_tarik, tgl_otorisasi, status_monitoring FROM db_gdcpay.tarik_saldo_auth"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res

def data_tarik_dana_auth_kd_member(kode_member= None, gdc_id= None):
    sql = f"SELECT * FROM db_gdcpay.tarik_saldo_auth WHERE kd_member= '{kode_member}' OR gdc_id= '{gdc_id}'"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_tarik_dana_exp():
    sql = f"SELECT * FROM db_gdcpay.tarik_dana_exp"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_tarik_dana_exp_kd_member(kode_member= None, gdc_id= None):
    sql = f"SELECT * FROM db_gdcpay.tarik_dana_exp WHERE kd_member= '{kode_member}' OR gdc_id= '{gdc_id}'"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_transaksi_merchant_auth():
    sql = f"SELECT * FROM db_gdcpay.transaksi_merchant_auth"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res

def data_transaksi_merchant_auth_kd_member(kode_member= None, gdc_id= None):
    sql = f"SELECT * FROM db_gdcpay.transaksi_merchant_auth WHERE kd_member= '{kode_member}' OR gdc_id= '{gdc_id}'"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_transaksi_merchant_exp():
    sql = f"SELECT * FROM db_gdcpay.transaksi_merchant_exp"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_transaksi_merchant_exp_kd_member(kode_member= None, gdc_id= None):
    sql = f"SELECT * FROM db_gdcpay.transaksi_merchant_exp WHERE kd_member= '{kode_member}' OR gdc_id= '{gdc_id}'"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_transfer_saldo_auth():
    sql = f"SELECT * FROM db_gdcpay.transfer_saldo_auth"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res

def data_transfer_saldo_auth_kd_member(nominal, kode_member_pengirim, kode_member_penerima):
    sql = f"SELECT * FROM db_gdcpay.transfer_saldo_auth WHERE (kd_member_penerima= '{kode_member_penerima}' and kd_member_pengirim= '{kode_member_pengirim}') and rp_transfer= '{nominal}' "
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    # return res.to_dict(orient='records')
    return res

def data_transfer_saldo_exp():
    sql = f"SELECT * FROM db_gdcpay.transfer_saldo_exp"
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')

def data_transfer_saldo_exp_kd_member(kode_member_penerima, kode_member_pengirim, gdc_id):
    sql = f"SELECT * FROM db_gdcpay.transfer_saldo_exp WHERE kd_member_penerima= '{kode_member_penerima}' OR kd_member_pengirim= '{kode_member_pengirim}' OR gdc_id= '{gdc_id}' "
    res = pd.read_sql(sql=sql, con=get_db_gdcpay())
    return res.to_dict(orient='records')


#mengambil database
def get_data_penerima_trf_saldo(kd_member_penerima):
    
    lst_member = "','".join(kd_member_penerima)
    sql = f"SELECT tgl_trx, nama_penerima, notelp_penerima, rp_transfer \
            FROM db_gdcpay.transfer_saldo_auth  \
            WHERE kd_member_penerima in ('{lst_member}')"
    data = pd.read_sql(sql, con=get_db_gdcpay())
    data['tgl_trx'] = pd.to_datetime(data['tgl_trx'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    return data    

def get_data_penerima_trf_merchant(kd_member):
    lst_member = "','".join(kd_member)
    sql = f"SELECT tgl_trx, nama_member, telp_member, rp_trx \
            FROM db_gdcpay.transaksi_merchant_auth  \
            WHERE kd_member in ('{lst_member}')"
    data = pd.read_sql(sql, con=get_db_gdcpay())
    data['tgl_trx'] = pd.to_datetime(data['tgl_trx'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    return data    

def get_data_penerima_trf_ppob(kd_member):
    lst_member = "','".join(kd_member)

    sql = f"SELECT tgl_trx, nama_member, no_telp_member, rp_trx \
            FROM db_gdcpay.riwayat_transaksi  \
            WHERE kd_member IN ('{lst_member}')"
    data = pd.read_sql(sql, con=get_db_gdcpay())
    data['tgl_trx'] = pd.to_datetime(data['tgl_trx'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    return data    

def get_data_penerima_tarik_dana(kd_member):
    lst_member = "','".join(kd_member)
    sql = f"SELECT tgl_tarik, nama_member, telp_member, rp_tarik \
            FROM db_gdcpay.tarik_saldo_auth  \
            WHERE kd_member in ('{lst_member}')"
    data = pd.read_sql(sql, con=get_db_gdcpay())
    data['tgl_tarik'] = pd.to_datetime(data['tgl_tarik'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    return data    

url = "http://localhost:5500"

#kalkulasi perhitungan saldo
def hitung_transfer_saldo():

    x = data_transfer_saldo_auth()
    b = x[['kd_member_pengirim', 'rp_transfer']]
    b['kd_member'] = b['kd_member_pengirim']

    lst_member_pengirim = b['kd_member'].to_list()

    a = data_member_gdc()
    a = a.loc[a['kd_member'].isin(lst_member_pengirim)]
    a = a[['kd_member', 'nama', 'notelp1', 'tgl_registrasi']]

    # grouping berdasarkan kd_member
    dt_concat = b.groupby('kd_member').agg({'kd_member_pengirim': 'count', 'rp_transfer': 'sum'}).reset_index()
    dt_concat['tgl_registrasi'] = a['tgl_registrasi']
    dt_concat = dt_concat.rename(columns={'kd_member_pengirim': 'count_trx'})

    dt_concat['riwayat'] = url+"/log_transfer_saldo"
    dt_concat['nominal'] = "nominal"

    dt_concat['notelp_pengirim'] = x['notelp_pengirim']
    dt_concat['nama_pengirim'] = x['nama_pengirim']
    dt_concat['notelp_penerima'] = x['notelp_penerima']
    dt_concat['nama_penerima'] = x['nama_penerima']
    dt_concat['kd_member_penerima'] = x['kd_member_penerima']
    dt_concat['kd_member_pengirim'] = x['kd_member_pengirim']
    dt_concat['status_monitoring'] = x['status_monitoring']

    periode = "2020-05"
    tgl_sekarang = datetime.now()
    date_and_time = pd.to_datetime(periode)
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] =  (dt_concat['tgl_registrasi'] - new_time).dt.days // 12

    dt_concat['jumlah_transaksi'] = dt_concat['count_trx']
    dt_concat['total_nominal_saldo'] = dt_concat['rp_transfer']
    dt_concat['rata2_nominal_transfer_saldo_per_transaksi'] = dt_concat['total_nominal_saldo'] / dt_concat['jumlah_transaksi']
    dt_concat['rata2_nominal_transfer_saldo_per_bulan'] = dt_concat['total_nominal_saldo'] / dt_concat['lama_akun_aktif']
    dt_concat['rata2_jumlah_transaksi_saldo_per_bulan'] = dt_concat['jumlah_transaksi'] / dt_concat['lama_akun_aktif']
    
    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    dt_concat = dt_concat.fillna("kosong")
    data = dt_concat.to_dict(orient='records')

    lst_kd_member = dt_concat['kd_member_penerima'].to_list()
    data_list = get_data_penerima_trf_saldo(lst_kd_member)
    angka = data_list['rp_transfer']
    max = angka.max()
    mean = angka.mean()
    data_list['deviasi'] = (max - mean) / (mean)

    for i in data:
        i['detail'] = data_list.loc[data_list['notelp_penerima'] == i['notelp_penerima']].to_dict(orient='records')

    return data

def hitung_transfer_saldo_by_filter(periode, nominal):

    x = data_transfer_saldo_auth()
    b = x[['kd_member_pengirim', 'rp_transfer']]
    b['kd_member'] = b['kd_member_pengirim']

    lst_member_pengirim = b['kd_member'].to_list()

    a = data_member_gdc()
    a = a.loc[a['kd_member'].isin(lst_member_pengirim)]
    a = a[['kd_member', 'nama', 'notelp1', 'tgl_registrasi']]

    # grouping berdasarkan kd_member
    dt_concat = b.groupby('kd_member').agg({'kd_member_pengirim': 'count', 'rp_transfer': 'sum'}).reset_index()
    dt_concat['tgl_registrasi'] = a['tgl_registrasi']
    dt_concat = dt_concat.rename(columns={'kd_member_pengirim': 'count_trx'})

    dt_concat['riwayat'] = url+"/log_transfer_saldo"
    dt_concat['nominal'] = int(nominal)
    dt_concat['notelp_pengirim'] = x['notelp_pengirim']
    dt_concat['nama_pengirim'] = x['nama_pengirim']
    dt_concat['notelp_penerima'] = x['notelp_penerima']
    dt_concat['nama_penerima'] = x['nama_penerima']
    dt_concat['kd_member_penerima'] = x['kd_member_penerima']
    dt_concat['kd_member_pengirim'] = x['kd_member_pengirim']
    dt_concat['status_monitoring'] = x['status_monitoring']

    tgl_sekarang = datetime.now()
    date_and_time = pd.to_datetime(periode)
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] =  (dt_concat['tgl_registrasi'] - new_time).dt.days // 12

    dt_concat['jumlah_transaksi'] = dt_concat['count_trx']
    dt_concat['total_nominal_saldo'] = dt_concat['rp_transfer']
    if int(nominal) >= dt_concat['total_nominal_saldo'].all():
        dt_concat['rata2_nominal_transfer_saldo_per_transaksi'] = dt_concat['total_nominal_saldo'] / dt_concat['jumlah_transaksi']
        dt_concat['rata2_nominal_transfer_saldo_per_bulan'] = dt_concat['total_nominal_saldo'] / dt_concat['lama_akun_aktif']
        dt_concat['rata2_jumlah_transaksi_saldo_per_bulan'] = dt_concat['jumlah_transaksi'] / dt_concat['lama_akun_aktif']

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    dt_concat = dt_concat.fillna("kosong")
    data = dt_concat.to_dict(orient='records')

    lst_kd_member = dt_concat['kd_member_penerima'].to_list()
    data_list = get_data_penerima_trf_saldo(lst_kd_member)
    angka = data_list['rp_transfer']
    max = angka.max()
    mean = angka.mean()
    data_list['deviasi'] = (max - mean) / (mean)


    for i in data:
        i['detail'] = data_list.loc[data_list['nama_penerima'] == i['nama_penerima']].to_dict(orient='records')
    return data

#kalkulasi transaksi merchant
def hitung_transaksi_merchant():
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'telp_member')
    merchant = data_transaksi_merchant_auth()
    dt_concat = merchant.merge(member, how="left", on= ['kd_member', 'nama_member', 'telp_member'])

    dt_concat['riwayat'] = url+"/log_transaksi_merchant" #construct
    dt_concat['nominal'] = "nilai_nominal" #construct

    dt_gbg = merchant.groupby('kd_member').agg({'nama_member': 'count', 'rp_trx': 'sum'}).reset_index()
    dt_gbg = dt_gbg.rename(columns={'nama_member': 'count_trx'})

    periode = "2020-2"
    date_and_time = pd.to_datetime(periode)
    tgl_sekarang = datetime.now()
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['jumlah_transaksi'] = dt_gbg['count_trx']
    dt_concat['total_nominal'] = dt_gbg['rp_trx']
    dt_concat['lama_akun_aktif'] = (dt_concat['tgl_registrasi'] - new_time)/np.timedelta64(1,'M')
    dt_concat['rata2_nominal_transaksi_per_bulan'] = dt_concat['total_nominal']/dt_concat['lama_akun_aktif']
    dt_concat['rata2_jumlah_transaksi_per_bulan'] = dt_concat['jumlah_transaksi']/dt_concat['lama_akun_aktif']
    dt_concat['rata2_nominal_per_transaksi'] = dt_concat['total_nominal']/dt_concat['jumlah_transaksi']

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    if dt_concat['st_member'].all() == 0:
        dt_concat['st_member'] = "unregistered"
    elif dt_concat['st_member'].all() == 1:
        dt_concat['st_member'] = "registered"

    lst_kd_member = dt_concat['kd_member']
    aplikasi_mrchnt = get_data_penerima_trf_merchant(lst_kd_member)
    angka = aplikasi_mrchnt['rp_trx']
    max = angka.max()
    mean = angka.mean()
    aplikasi_mrchnt['deviasi'] = (max - mean) / (mean)


    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')

    for x in data:
        x['detail'] = aplikasi_mrchnt.loc[aplikasi_mrchnt['nama_member'] == x['nama_member']].to_dict(orient='records')

    return data

def hitung_transaksi_merchant_by_filter(periode, nominal):
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'telp_member')
    merchant = data_transaksi_merchant_auth()
    dt_concat = merchant.merge(member, how="left", on= ['kd_member', 'nama_member', 'telp_member'])
    dt_concat['riwayat'] = url+"/log_transaksi_merchant" #construct
    dt_concat['nominal'] = int(nominal)

    dt_gbg = merchant.groupby('kd_member').agg({'nama_member': 'count', 'rp_trx': 'sum'}).reset_index()
    dt_gbg = dt_gbg.rename(columns={'nama_member': 'count_trx'})


    date_and_time = pd.to_datetime(periode)
    tgl_sekarang = datetime.now()
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] = (dt_concat['tgl_registrasi'] - new_time)/np.timedelta64(1,'M')

    dt_concat['jumlah_transaksi'] = dt_gbg['count_trx']
    dt_concat['total_nominal'] = dt_gbg['rp_trx']
    if int(nominal) >= dt_concat['total_nominal'].all():
        dt_concat['rata2_nominal_transaksi_per_bulan'] = dt_concat['total_nominal']/dt_concat['lama_akun_aktif']
        dt_concat['rata2_jumlah_transaksi_per_bulan'] = dt_concat['jumlah_transaksi']/dt_concat['lama_akun_aktif']
        dt_concat['rata2_nominal_per_transaksi'] = dt_concat['total_nominal']/dt_concat['jumlah_transaksi']


    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    if dt_concat['st_member'].all() == 0:
        dt_concat['st_member'] = "unregistered"
    elif dt_concat['st_member'].all() == 1:
        dt_concat['st_member'] = "registered"

    lst_kd_member = dt_concat['kd_member']
    aplikasi_mrchnt = get_data_penerima_trf_merchant(lst_kd_member)
    angka = aplikasi_mrchnt['rp_trx']
    max = angka.max()
    mean = angka.mean()
    aplikasi_mrchnt['deviasi'] = (max - mean) / (mean)


    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')
    for x in data:
        x['detail'] = aplikasi_mrchnt.loc[aplikasi_mrchnt['nama_member'] == x['nama_member']].to_dict(orient='records')    

    return data

#kalkulasi perhitungan ppob
def hitung_ppob():
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'no_telp_member')
    riwayat = data_riwayat_transaksi()
    dt_concat = riwayat.merge(member, how="left", on= ['kd_member', 'nama_member', 'no_telp_member'])

    dt_concat['riwayat'] = url+"/log_ppob" #construct
    dt_concat['nominal'] = "data nominal"

    if dt_concat['syarat'].all() == 1:
        dt_concat['syarat'] = 'terverifikasi'
    elif dt_concat['syarat'].all() == 0:
        dt_concat['syarat'] = 'belum terverifikasi'
    else:
        dt_concat['syarat'] = 'belum terlaporkan'

    if dt_concat['st_member'].all() == 1:
        dt_concat['st_member'] = 'registered'
    elif dt_concat['st_member'].all() == 0:
        dt_concat['st_member'] = 'unregistered'
    else:
        dt_concat['st_member'] = 'unknowm'

    dt_gbg = riwayat.groupby('kd_member').agg({'nama_member': 'count', 'rp_trx': 'sum'}).reset_index()
    dt_gbg = dt_gbg.rename(columns={'nama_member': 'count_trx'})

    periode = "2020-05"
    date_and_time = pd.to_datetime(periode)
    tgl_sekarang = datetime.now()
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] = (dt_concat['tgl_registrasi'] - new_time)/np.timedelta64(1,'M')

    dt_concat['jumlah_transaksi'] = dt_gbg['count_trx']
    dt_concat['total_nominal'] = dt_gbg['rp_trx']
    dt_concat['rata2_nominal_transaksi_per_bulan'] = dt_concat['total_nominal']/dt_concat['lama_akun_aktif']
    dt_concat['rata2_jumlah_transaksi_per_bulan'] = dt_concat['jumlah_transaksi']/dt_concat['lama_akun_aktif']
    dt_concat['rata2_nominal_per_transaksi'] = dt_concat['total_nominal']/dt_concat['jumlah_transaksi']


    lst_kd_member = dt_concat['kd_member']
    aplikasi_ppob = get_data_penerima_trf_ppob(lst_kd_member)
    angka = aplikasi_ppob['rp_trx']
    max = angka.max()
    mean = angka.mean()
    aplikasi_ppob['deviasi'] = (max - mean) / (mean)


    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')

    for i in data:
        i['detail'] = aplikasi_ppob.loc[aplikasi_ppob['nama_member'] == i['nama_member']].to_dict(orient='records')
    return data

def hitung_ppob_by_filter(periode, nominal):    
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'no_telp_member')
    riwayat = data_riwayat_transaksi()
    dt_concat = riwayat.merge(member, how="left", on= ['kd_member', 'nama_member', 'no_telp_member'])

    dt_concat['riwayat'] = url+"/log_ppob" #construct
    dt_concat['nominal'] = int(nominal)

    if dt_concat['syarat'].all() == 1:
        dt_concat['syarat'] = 'terverifikasi'
    elif dt_concat['syarat'].all() == 0:
        dt_concat['syarat'] = 'belum terverifikasi'
    else:
        dt_concat['syarat'] = 'belum terlaporkan'

    if dt_concat['st_member'].all() == 1:
        dt_concat['st_member'] = 'registered'
    elif dt_concat['st_member'].all() == 0:
        dt_concat['st_member'] = 'unregistered'
    else:
        dt_concat['st_member'] = 'unknowm'

    dt_gbg = riwayat.groupby('kd_member').agg({'nama_member': 'count', 'rp_trx': 'sum'}).reset_index()
    dt_gbg = dt_gbg.rename(columns={'nama_member': 'count_trx'})

    date_and_time = pd.to_datetime(periode)
    tgl_sekarang = datetime.now()
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] = (dt_concat['tgl_registrasi'] - new_time)/np.timedelta64(1,'M')

    dt_concat['jumlah_transaksi'] = dt_gbg['count_trx']
    dt_concat['total_nominal'] = dt_gbg['rp_trx']
    if int(nominal) >= dt_concat['total_nominal'].all():
        dt_concat['rata2_nominal_transaksi_per_bulan'] = dt_concat['total_nominal']/dt_concat['lama_akun_aktif']
        dt_concat['rata2_jumlah_transaksi_per_bulan'] = dt_concat['jumlah_transaksi']/dt_concat['lama_akun_aktif']
        dt_concat['rata2_nominal_per_transaksi'] = dt_concat['total_nominal']/dt_concat['jumlah_transaksi']


    lst_kd_member = dt_concat['kd_member']

    aplikasi_ppob = get_data_penerima_trf_ppob(lst_kd_member)
    angka = aplikasi_ppob['rp_trx']
    max = angka.max()
    mean = angka.mean()
    aplikasi_ppob['deviasi'] = (max - mean) / (mean)


    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')

    for i in data:
        i['detail'] = aplikasi_ppob.loc[aplikasi_ppob['nama_member'] == i['nama_member']].to_dict(orient='records')

    return data

#kalkulasi perhitungan tarik dana
def hitung_tarik_dana():
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'telp_member')
    tarikDana = data_tarik_dana_auth()
    dt_concat = tarikDana.merge(member, how="left", on= ['kd_member', 'nama_member', 'telp_member'])

    dt_concat['riwayat'] = url+"/log_tarik_dana" #construct
    dt_concat['nominal'] = "nilai nominal" #construct

    dt_gbg = tarikDana.groupby('kd_member').agg({'nama_member': 'count', 'rp_tarik': 'sum'}).reset_index()
    dt_gbg = dt_gbg.rename(columns={'nama_member': 'count_trx'})

    periode = "2020-05"
    date_and_time = pd.to_datetime(periode)
    tgl_sekarang = datetime.now()
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] = (dt_concat['tgl_registrasi'] - new_time)/np.timedelta64(1,'M')

    dt_concat['jumlah_transaksi'] = dt_gbg['count_trx']
    dt_concat['total_nominal'] = dt_gbg['rp_tarik']
    
    dt_concat['rata2_nominal_transaksi_per_bulan'] = dt_concat['total_nominal']/dt_concat['lama_akun_aktif']
    dt_concat['rata2_jumlah_transaksi_per_bulan'] = dt_concat['jumlah_transaksi']/dt_concat['lama_akun_aktif']
    dt_concat['rata2_nominal_per_transaksi'] = dt_concat['total_nominal']/dt_concat['jumlah_transaksi']

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    lst_kd_member = dt_concat['kd_member']
    aplikasi_tarik_dana = get_data_penerima_tarik_dana(lst_kd_member)
    angka = aplikasi_tarik_dana['rp_tarik']
    max = angka.max()
    mean = angka.mean()
    aplikasi_tarik_dana['deviasi'] = (max - mean) / (mean)

    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')

    for i in data:
        i['detail'] = aplikasi_tarik_dana.loc[aplikasi_tarik_dana['nama_member'] == i['nama_member']].to_dict(orient='records')

    return data

def hitung_tarik_dana_by_filter(periode, nominal):
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'telp_member')
    tarikDana = data_tarik_dana_auth()
    dt_concat = tarikDana.merge(member, how="left", on= ['kd_member', 'nama_member', 'telp_member'])

    dt_concat['riwayat'] = url+"/log_tarik_dana" #construct
    dt_concat['nominal'] = int(nominal) #construct

    dt_gbg = tarikDana.groupby('kd_member').agg({'nama_member': 'count', 'rp_tarik': 'sum'}).reset_index()
    dt_gbg = dt_gbg.rename(columns={'nama_member': 'count_trx'})

    date_and_time = pd.to_datetime(periode)
    tgl_sekarang = datetime.now()
    time_change = timedelta(days= tgl_sekarang.day)
    new_time = date_and_time + time_change
    dt_concat['lama_akun_aktif'] = (dt_concat['tgl_registrasi'] - new_time)/np.timedelta64(1,'M')

    dt_concat['jumlah_transaksi'] = dt_gbg['count_trx']
    dt_concat['total_nominal'] = dt_gbg['rp_tarik']
    if int(nominal) >= dt_concat['total_nominal'].all():
        dt_concat['rata2_nominal_transaksi_per_bulan'] = dt_concat['total_nominal']/dt_concat['lama_akun_aktif']
        dt_concat['rata2_jumlah_transaksi_per_bulan'] = dt_concat['jumlah_transaksi']/dt_concat['lama_akun_aktif']
        dt_concat['rata2_nominal_per_transaksi'] = dt_concat['total_nominal']/dt_concat['jumlah_transaksi']

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    lst_kd_member = dt_concat['kd_member']
    aplikasi_tarik_dana = get_data_penerima_tarik_dana(lst_kd_member)
    angka = aplikasi_tarik_dana['rp_tarik']
    max = angka.max()
    mean = angka.mean()
    aplikasi_tarik_dana['deviasi'] = (max - mean) / (mean)


    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')
    for i in data:
        i['detail'] = aplikasi_tarik_dana.loc[aplikasi_tarik_dana['nama_member'] == i['nama_member']].to_dict(orient='records')

    return data



# log riwayat
def log_riwayat_transfer_saldo():
    transfer = data_transfer_saldo_auth()
    member = data_member_gdc()
    dt_concat = pd.concat([transfer, member], axis= 1)
    dt_concat['tanggal_dan_waktu_verifikasi'] = "undefined"
    dt_concat['id_staff_manrisk'] = "undefined"
    dt_concat['nama_staff_manrisk'] = "undefined"
    dt_concat['tanggal_dan_waktu_otorisasi'] = "undefined"
    dt_concat['id_manajer_kepatuhan'] = "undefined"
    dt_concat['nama_manajer_kepatuhan'] = "undefined"
    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')
    
    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    return data

def riwayat_log_transaksi_merchant():
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'telp_member')
    merchant = data_transaksi_merchant_auth()
    dt_concat = pd.concat([member, merchant], axis= 0)
    dt_concat['tgl_pembayaran'] = pd.to_datetime(dt_concat['tgl_pembayaran'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    dt_concat['tanggal_dan_waktu_verifikasi'] = 'undefined'
    dt_concat['id_staff_manrisk'] = 'undefined'
    dt_concat['nama_staff_manrisk'] = 'undefined'
    dt_concat['tanggal_dan_waktu_otorisasi'] = 'undefined'
    dt_concat['id_manajer_kepatuhan'] = 'undefined'
    dt_concat['nama_manajer_kepatuhan'] = 'undefined'

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"
    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')
    return data

def riwayat_log_ppob():
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'no_telp_member')
    riwayat = data_riwayat_transaksi()
    dt_concat = pd.concat([member, riwayat], axis= 0)
    dt_concat['tgl_trx'] = pd.to_datetime(dt_concat['tgl_trx'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    dt_concat['tanggal_dan_waktu_verifikasi'] = "undefined"
    dt_concat['id_staff_manrisk'] = "undefined"
    dt_concat['nama_staff_manrisk'] = "undefined"
    dt_concat['tanggal_dan_waktu_otorisasi'] = "undefined"
    dt_concat['id_manajer_kepatuhan'] = "undefined"
    dt_concat['nama_manajer_kepatuhan'] = "undefined"

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"

    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')
    return data

def riwayat_log_tarik_dana():
    member = data_member_gdc()
    member.columns = member.columns.str.replace('nama', 'nama_member')
    member.columns = member.columns.str.replace('notelp1', 'telp_member')
    tarikDana = data_tarik_dana_auth()
    dt_concat = pd.concat([member, tarikDana], axis= 0)
    dt_concat['tgl_tarik'] = pd.to_datetime(dt_concat['tgl_tarik'], errors = 'coerce',format = '%Y-%m-%d').dt.strftime("%d-%m-%Y %H:%M:%S")
    dt_concat['tanggal_dan_waktu_verifikasi'] = "undefined"
    dt_concat['nama_staff_manrisk'] = "undefined"
    dt_concat['tanggal_dan_waktu_otorisasi'] = "undefined"
    dt_concat['id_manajer_kepatuhan'] = "undefined"
    dt_concat['nama_manajer_kepatuhan'] = "undefined"

    if dt_concat['status_monitoring'].all() == "0":
        dt_concat['status_monitoring'] = "belum verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "1":
        dt_concat['status_monitoring'] = "verifikasi manrisk"
    elif dt_concat['status_monitoring'].all() == "2":
        dt_concat['status_monitoring'] = "proses monitoring selesai"
    else:
        dt_concat['status_monitoring'] = "undefined"    

    dt_concat = dt_concat.fillna("kosong")
    data =  dt_concat.to_dict(orient='records')
    return data