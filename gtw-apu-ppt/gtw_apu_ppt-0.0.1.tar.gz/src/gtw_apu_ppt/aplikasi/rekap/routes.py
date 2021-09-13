import os

from numpy import datetime_as_string
import trafaret as tr
import pandas as pd
from datetime import date, datetime
from aplikasi.rekap import blueprint
from aplikasi.utils import to_client
from aplikasi.rekap.controller import *
from werkzeug.utils import secure_filename
from flask import request, current_app as app

def member_gdc():
    user = data_member_gdc()
    data = []
    for k in user:
        if k['tgl_registrasi'] is not None:
            data_tgl = str(k['tgl_registrasi'])
            tgl_registrasi = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_registrasi = ''
            
        data.append({
            'kd_member': k['kd_member'],
            'syarat': k['syarat'],
            'nama': k['nama'],
            'notelp1': int(k['notelp1']),
            'tgl_registrasi': k['tgl_registrasi'],
            'tgl_registrasi': tgl_registrasi,
            'kode_akses': k['kode_akses'],
            'pin': k['pin'],
            'st_member': int(k['st_member']),
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': data}
    if len(data)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def member_gdc_kd_member(kd_member= None):
    user = data_member_gdc_kd_member(kode_member= kd_member)
    data = []
    for k in user:
        if k['tgl_registrasi'] is not None:
            data_tgl = str(k['tgl_registrasi'])
            tgl_registrasi = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_registrasi = ''
        data.append({
            'kd_member': k['kd_member'],
            'syarat': k['syarat'],
            'nama': k['nama'],
            'notelp1': int(k['notelp1']),
            'tgl_registrasi': tgl_registrasi,
            'kode_akses': k['kode_akses'],
            'pin': k['pin'],
            'st_member': int(k['st_member']),
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': data}
    if len(data)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def member_gdc_disabled():
    user_disabled = data_member_gdc_disabled()
    data_disabled = []
    for num in user_disabled:
        if num['tgl_registrasi'] is not None:
            data_tgl = str(num['tgl_registrasi'])
            tgl_registrasi = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_registrasi = ''
        data_disabled.append({
            'kd_member': num['kd_member'],
            'syarat': num['syarat'],
            'nama': num['nama'],
            'notelp1': int(num['notelp1']),
            'tgl_registrasi': tgl_registrasi,
            'kode_akses': num['kode_akses'],
            'pin': num['pin'],
            'st_member': int(num['st_member']),
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': data_disabled}
    if len(data_disabled)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def member_gdc_disabled_kd_member(kd_member= None):
    user_disabled = data_member_gdc_disabled_kd_member(kode_member= kd_member)
    data_disabled = []
    for num in user_disabled:
        if num['tgl_registrasi'] is not None:
            data_tgl = str(num['tgl_registrasi'])
            tgl_registrasi = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_registrasi = ''
        data_disabled.append({
            'kd_member': num['kd_member'],
            'syarat': num['syarat'],
            'nama': num['nama'],
            'notelp1': int(num['notelp1']),
            'tgl_registrasi': tgl_registrasi,
            'kode_akses': num['kode_akses'],
            'pin': num['pin'],
            'st_member': int(num['st_member']),
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': data_disabled}
    if len(data_disabled)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def riwayat_transaksi():
    riwayat_transaksi = data_riwayat_transaksi()
    data_riwayat = []
    for num in riwayat_transaksi:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        data_riwayat.append({
            'partition_id': int(num['partition_id']),
            'kd_member': num['kd_member'],
            'no_telp_member': int(num['no_telp_member']),
            'nama_member': num['nama_member'],
            'gdc_id': num['gdc_id'],
            'jenis_trx': num['jenis_trx'],
            'status_trx': num['status_trx'],
            'metode_bayar': num['metode_bayar'],
            'tgl_trx': tgl_trx,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': data_riwayat}
    if len(data_riwayat)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def riwayat_transaksi_kd_member(kd_member= None, gdc_id= None):
    riwayat_transaksi = data_riwayat_transaksi_kd_member(kode_member= kd_member, gdc_id= gdc_id)
    data_riwayat = []
    for num in riwayat_transaksi:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''
        data_riwayat.append({
            'partition_id': int(num['partition_id']),
            'kd_member': num['kd_member'],
            'no_telp_member': int(num['no_telp_member']),
            'nama_member': num['nama_member'],
            'gdc_id': num['gdc_id'],
            'jenis_trx': num['jenis_trx'],
            'status_trx': num['status_trx'],
            'metode_bayar': num['metode_bayar'],
            'tgl_trx': tgl_trx,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': data_riwayat}
    if len(data_riwayat)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def saldo():
    saldo = data_saldo()
    dt_saldo = []
    for num in saldo:
        if num['last_update'] is not None:
            data_tgl = str(num['last_update'])
            last_update = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            last_update = ''

        dt_saldo.append({
            'kd_member': num['kd_member'],
            'rp_saldo': num['rp_saldo'],
            'jml_poin': int(num['jml_poin']),
            'last_update': last_update,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_saldo}
    if len(dt_saldo)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def saldo_kd_member(kd_member= None):
    saldo = data_saldo_kd_member(kode_member= kd_member)
    dt_saldo = []
    for num in saldo:
        if num['last_update'] is not None:
            data_tgl = str(num['last_update'])
            last_update = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            last_update = ''

        dt_saldo.append({
            'kd_member': num['kd_member'],
            'rp_saldo': num['rp_saldo'],
            'jml_poin': int(num['jml_poin']),
            'last_update': last_update,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_saldo}
    if len(dt_saldo)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def saldo_blokir():
    saldo_blokir = data_saldo_blokir()
    dt_saldo_blkr = []
    for num in saldo_blokir:
        if num['tgl_transaksi'] is not None:
            data_tgl = str(num['tgl_transaksi'])
            tgl_transaksi = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_transaksi = ''
        dt_saldo_blkr.append({
            'kd_member': num['kd_member'],
            'gdc_id': num['gdc_id'],
            'tgl_transaksi': tgl_transaksi,
            'deskripsi': num['deskripsi'],
            'debet': num['debet'],
            'kredit': num['kredit'],
            'jml_poin': int(num['jml_poin']),
            'pendapatan': int(num['pendapatan']),
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_saldo_blkr}
    if len(dt_saldo_blkr)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def saldo_blokir_kd_member(kd_member= None, gdc_id= None):
    saldo_blokir = data_saldo_blokir_kd_member(kode_member= kd_member, gdc_id= gdc_id)
    dt_saldo_blkr = []
    for num in saldo_blokir:
        if num['tgl_transaksi'] is not None:
            data_tgl = str(num['tgl_transaksi'])
            tgl_transaksi = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_transaksi = ''
        dt_saldo_blkr.append({
            'kd_member': num['kd_member'],
            'gdc_id': num['gdc_id'],
            'tgl_transaksi': tgl_transaksi,
            'deskripsi': num['deskripsi'],
            'debet': num['debet'],
            'kredit': num['kredit'],
            'jml_poin': int(num['jml_poin']),
            'pendapatan': int(num['pendapatan']),
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_saldo_blkr}
    if len(dt_saldo_blkr)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def tarik_dana_auth():
    tarik_dana_auth = data_tarik_dana_auth()
    dt_trk_dana_auth = []
    for num in tarik_dana_auth:
        dt_trk_dana_auth.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'device_id': num['device_id'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'telp_member': int(num['telp_member']),
            'bank': num['bank'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_dana_auth}
    if len(dt_trk_dana_auth)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def tarik_dana_auth_kd_member(kd_member= None, gdc_id= None):
    tarik_dana_auth = data_tarik_dana_auth_kd_member(kode_member= kd_member, gdc_id= gdc_id)
    dt_trk_dana_auth = []
    for num in tarik_dana_auth:
        dt_trk_dana_auth.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'device_id': num['device_id'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'telp_member': int(num['telp_member']),
            'bank': num['bank'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_dana_auth}
    if len(dt_trk_dana_auth)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def tarik_dana_exp():
    tarik_dana_exp = data_tarik_dana_exp()
    dt_trk_dana_exp = []
    for num in tarik_dana_exp:
        if num['tgl_tarik'] is not None:
            data_tgl = str(num['tgl_tarik'])
            tgl_tarik = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_tarik = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        dt_trk_dana_exp.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'device_id': num['device_id'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'bank': num['bank'],
            'norek': num['norek'],
            'nama_norek': num['nama_norek'],
            'rp_tarik': int(num['rp_tarik']),
            'rp_biaya': int(num['rp_biaya']),
            'tgl_tarik': tgl_tarik,
            'tgl_expired': tgl_expired,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_dana_exp}
    if len(dt_trk_dana_exp)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def tarik_dana_exp_kd_member(kd_member= None, gdc_id= None):
    tarik_dana_exp = data_tarik_dana_exp_kd_member(kode_member= kd_member, gdc_id= gdc_id)
    dt_trk_dana_exp = []
    for num in tarik_dana_exp:
        if num['tgl_tarik'] is not None:
            data_tgl = str(num['tgl_tarik'])
            tgl_tarik = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_tarik = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        dt_trk_dana_exp.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'device_id': num['device_id'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'bank': num['bank'],
            'norek': num['norek'],
            'nama_norek': num['nama_norek'],
            'rp_tarik': int(num['rp_tarik']),
            'rp_biaya': int(num['rp_biaya']),
            'tgl_tarik': tgl_tarik,
            'tgl_expired': tgl_expired,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_dana_exp}
    if len(dt_trk_dana_exp)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transaksi_merchant_auth():
    transaksi_merchant_auth = data_transaksi_merchant_auth()
    dt_trk_merchant_auth = []
    for num in transaksi_merchant_auth:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_tarik = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        if num['tgl_pembayaran'] is not None:
            data_tgl = str(num['tgl_pembayaran'])
            tgl_pembayaran = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_pembayaran = ''

        dt_trk_merchant_auth.append({
            'kd_app': num['kd_app'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'telp_member': int(num['telp_member']),
            'gdc_id': num['gdc_id'],
            'kd_merchant': num['kd_merchant'],
            'kd_client': num['kd_client'],
            'nama_merchant': num['nama_merchant'],
            'telp_merchant': int(num['telp_merchant']),
            'qr_code_merchant': num['qr_code_merchant'],
            'rp_trx': num['rp_trx'],
            'rp_biaya': num['rp_biaya'],
            'tgl_expired': tgl_expired,
            'tgl_trx': tgl_trx,
            'tgl_pembayaran': tgl_pembayaran,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_merchant_auth}
    if len(dt_trk_merchant_auth)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transaksi_merchant_auth_kd_member(kd_member= None, gdc_id= None):
    transaksi_merchant_auth = data_transaksi_merchant_auth_kd_member(kode_member= kd_member, gdc_id= gdc_id)
    dt_trk_merchant_auth = []
    for num in transaksi_merchant_auth:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        if num['tgl_pembayaran'] is not None:
            data_tgl = str(num['tgl_pembayaran'])
            tgl_pembayaran = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_pembayaran = ''

        dt_trk_merchant_auth.append({
            'kd_app': num['kd_app'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'telp_member': int(num['telp_member']),
            'gdc_id': num['gdc_id'],
            'kd_merchant': num['kd_merchant'],
            'kd_client': num['kd_client'],
            'nama_merchant': num['nama_merchant'],
            'telp_merchant': int(num['telp_merchant']),
            'qr_code_merchant': num['qr_code_merchant'],
            'rp_trx': num['rp_trx'],
            'rp_biaya': num['rp_biaya'],
            'tgl_expired': tgl_expired,
            'tgl_trx': tgl_trx,
            'tgl_pembayaran': tgl_pembayaran,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_merchant_auth}
    if len(dt_trk_merchant_auth)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transaksi_merchant_exp():
    transaksi_merchant_exp = data_transaksi_merchant_exp()
    dt_trk_merchant_exp = []
    for num in transaksi_merchant_exp:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''
            
        dt_trk_merchant_exp.append({
            'kd_app': num['kd_app'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'telp_member': int(num['telp_member']),
            'gdc_id': num['gdc_id'],
            'kd_merchant': num['kd_merchant'],
            'kd_client': num['kd_client'],
            'nama_merchant': num['nama_merchant'],
            'telp_merchant': int(num['telp_merchant']),
            'qr_code_merchant': num['qr_code_merchant'],
            'rp_trx': num['rp_trx'],
            'rp_biaya': num['rp_biaya'],
            'tgl_expired': tgl_expired,
            'tgl_trx': tgl_trx,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_merchant_exp}
    if len(dt_trk_merchant_exp)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transaksi_merchant_exp_kd_member(kd_member= None, gdc_id= None):
    transaksi_merchant_exp = data_transaksi_merchant_exp_kd_member(kode_member= kd_member, gdc_id = gdc_id)
    dt_trk_merchant_exp = []
    for num in transaksi_merchant_exp:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        dt_trk_merchant_exp.append({
            'kd_app': num['kd_app'],
            'kd_member': num['kd_member'],
            'nama_member': num['nama_member'],
            'telp_member': int(num['telp_member']),
            'gdc_id': num['gdc_id'],
            'kd_merchant': num['kd_merchant'],
            'kd_client': num['kd_client'],
            'nama_merchant': num['nama_merchant'],
            'telp_merchant': int(num['telp_merchant']),
            'qr_code_merchant': num['qr_code_merchant'],
            'rp_trx': num['rp_trx'],
            'rp_biaya': num['rp_biaya'],
            'tgl_expired': tgl_expired,
            'tgl_trx': tgl_trx,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_merchant_exp}
    if len(dt_trk_merchant_exp)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transfer_saldo_auth():
    transaksi_merchant_auth = data_transfer_saldo_auth()
    dt_trk_merchant_auth = []
    for num in transaksi_merchant_auth:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''
        
        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        dt_trk_merchant_auth.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'kd_member_pengirim': num['kd_member_pengirim'],
            'kd_member_penerima': num['kd_member_penerima'],
            'notelp_pengirim': int(num['notelp_pengirim']),
            'notelp_penerima': int(num['notelp_penerima']),
            'nama_pengirim': num['nama_pengirim'],
            'nama_penerima': num['nama_penerima'],
            'berita': num['berita'],
            'rp_transfer': num['rp_transfer'],
            'rp_biaya': num['rp_biaya'],
            'tgl_trx': tgl_trx,
            'tgl_expired': tgl_expired,
            # 'tgl_trx': num['tgl_trx'],
            # 'tgl_expired': num['tgl_expired'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_merchant_auth}
    if len(dt_trk_merchant_auth)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transfer_saldo_auth_kd_member(kd_member_penerima = None, kd_member_pengirim= None, gdc_id= None):
    transaksi_merchant_auth = data_transfer_saldo_auth_kd_member(kode_member_penerima= kd_member_penerima, kode_member_pengirim= kd_member_penerima, gdc_id= gdc_id)
    dt_trk_merchant_auth = []
    for num in transaksi_merchant_auth:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''
        dt_trk_merchant_auth.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'kd_member_pengirim': num['kd_member_pengirim'],
            'kd_member_penerima': num['kd_member_penerima'],
            'notelp_pengirim': int(num['notelp_pengirim']),
            'notelp_penerima': int(num['notelp_penerima']),
            'nama_pengirim': num['nama_pengirim'],
            'nama_penerima': num['nama_penerima'],
            'berita': num['berita'],
            'rp_transfer': num['rp_transfer'],
            'rp_biaya': num['rp_biaya'],
            'tgl_trx': tgl_trx,
            'tgl_expired': tgl_expired,
            # 'tgl_trx': num['tgl_trx'],
            # 'tgl_expired': num['tgl_expired'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_merchant_auth}
    if len(dt_trk_merchant_auth)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transfer_saldo_exp():
    transfer_saldo_exp = data_transfer_saldo_exp()
    dt_trk_saldo_exp = []
    for num in transfer_saldo_exp:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        dt_trk_saldo_exp.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'kd_member_pengirim': num['kd_member_pengirim'],
            'kd_member_penerima': num['kd_member_penerima'],
            'notelp_pengirim': int(num['notelp_pengirim']),
            'notelp_penerima': int(num['notelp_penerima']),
            'nama_pengirim': num['nama_pengirim'],
            'nama_penerima': num['nama_penerima'],
            'berita': num['berita'],
            'rp_transfer': num['rp_transfer'],
            'rp_biaya': num['rp_biaya'],
            'tgl_trx': tgl_trx,
            'tgl_expired': tgl_expired,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_saldo_exp}
    if len(dt_trk_saldo_exp)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

def transfer_saldo_exp_kd_member(kd_member_penerima= None, kd_member_pengirim= None, gdc_id= None):
    transfer_saldo_exp = data_transfer_saldo_exp_kd_member(kode_member_penerima= kd_member_penerima, kode_member_pengirim= kd_member_pengirim, gdc_id= gdc_id)
    dt_trk_saldo_exp = []
    for num in transfer_saldo_exp:
        if num['tgl_trx'] is not None:
            data_tgl = str(num['tgl_trx'])
            tgl_trx = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_trx = ''

        if num['tgl_expired'] is not None:
            data_tgl = str(num['tgl_expired'])
            tgl_expired = datetime.strptime(data_tgl, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
        else:
            tgl_expired = ''

        dt_trk_saldo_exp.append({
            'gdc_id': num['gdc_id'],
            'app_id': num['app_id'],
            'kd_member_pengirim': num['kd_member_pengirim'],
            'kd_member_penerima': num['kd_member_penerima'],
            'notelp_pengirim': int(num['notelp_pengirim']),
            'notelp_penerima': int(num['notelp_penerima']),
            'nama_pengirim': num['nama_pengirim'],
            'nama_penerima': num['nama_penerima'],
            'berita': num['berita'],
            'rp_transfer': num['rp_transfer'],
            'rp_biaya': num['rp_biaya'],
            'tgl_trx': tgl_trx,
            'tgl_expired': tgl_expired,
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_trk_saldo_exp}
    if len(dt_trk_saldo_exp)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)



@blueprint.route('/kalkulasi_transfer_saldo', methods=['GET', ])
def kalkulasi_transfer_saldo():
    data_hasil_hitung = hitung_transfer_saldo()
    dt_htg = []
    for num in data_hasil_hitung:
        dt_htg.append({
            # 'deviasi': num['deviasi'],
            'nominal': num['nominal'],
            'notelp_pengirim': num['notelp_pengirim'],
            'nama_pengirim': num['nama_pengirim'],
            'notelp_penerima': num['notelp_penerima'],
            'nama_penerima': num['nama_penerima'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'kd_member_penerima': num['kd_member_penerima'],
            'kd_member_pengirim': num['kd_member_pengirim'],
            'total_nominal_saldo': num['total_nominal_saldo'],

            'lama_akun_aktif': num['lama_akun_aktif'],
            'rata2_jumlah_transaksi_saldo_per_bulan': num['rata2_jumlah_transaksi_saldo_per_bulan'],
            'rata2_nominal_transfer_saldo_per_bulan': num['rata2_nominal_transfer_saldo_per_bulan'],
            'rata2_nominal_transfer_saldo_per_transaksi': num['rata2_nominal_transfer_saldo_per_transaksi'],
            'riwayat': num['riwayat'],
            'status_monitoring': num['status_monitoring'],
            'detail': num['detail'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_transfer_saldo/<data_periode>/<data_nominal>', methods=['GET', ])
def kalkulasi_transfer_saldo_by_filter(data_periode= None, data_nominal= None):
    data_hasil_hitung = hitung_transfer_saldo_by_filter(periode= data_periode, nominal= data_nominal)
    dt_htg = []

    for num in data_hasil_hitung:
            
        dt_htg.append({
            'nominal': num['nominal'],
            'notelp_pengirim': num['notelp_pengirim'],
            'nama_pengirim': num['nama_pengirim'],
            'notelp_penerima': num['notelp_penerima'],
            'nama_penerima': num['nama_penerima'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'kd_member_penerima': num['kd_member_penerima'],
            'kd_member_pengirim': num['kd_member_pengirim'],
            'total_nominal_saldo': num['total_nominal_saldo'],

            'lama_akun_aktif': num['lama_akun_aktif'],
            'rata2_jumlah_transaksi_saldo_per_bulan': num['rata2_jumlah_transaksi_saldo_per_bulan'],
            'rata2_nominal_transfer_saldo_per_bulan': num['rata2_nominal_transfer_saldo_per_bulan'],
            'rata2_nominal_transfer_saldo_per_transaksi': num['rata2_nominal_transfer_saldo_per_transaksi'],
            'riwayat': num['riwayat'],
            'status_monitoring': num['status_monitoring'],
            'detail': num['detail'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/log_transfer_saldo', methods=['GET', ])
def log_transfer_saldo():
    data_hasil_hitung = log_riwayat_transfer_saldo()
    dt_htg = []

    for num in data_hasil_hitung:
            
        dt_htg.append({
            'tanggal_dan_waktu': num['tgl_trx'],
            'nama_pengirim': num['nama_pengirim'],
            'id_pengirim': num['kd_member_pengirim'],
            'nomor_pengirim': num['notelp_pengirim'],
            'nama_penerima': num['nama_penerima'],
            'id_penerima': num['kd_member_penerima'],
            'nomor_penerima': num['notelp_penerima'],
            'tanggal_dan_waktu_verifikasi': num['tanggal_dan_waktu_verifikasi'],
            'id_staff_manrisk': num['id_staff_manrisk'],
            'nama_staff_manrisk': num['nama_staff_manrisk'],
            'tanggal_dan_waktu_otorisasi': num['tanggal_dan_waktu_otorisasi'],
            'id_manajer_kepatuhan': num['id_manajer_kepatuhan'],
            'nama_manajer_kepatuhan': num['nama_manajer_kepatuhan'],
            'status': num['status_monitoring'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_transaksi_merchant', methods=['GET', ])
def kalkulasi_transaksi_merchant():
    data_hasil_hitung = hitung_transaksi_merchant()
    dt_htg = []

    for num in data_hasil_hitung:   
        dt_htg.append({
            'st_member': num['st_member'],
            'telp_member': num['telp_member'],
            'nama_member': num['nama_member'],
            'nominal': num['nominal'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],
            'lama_akun_aktif': num['lama_akun_aktif'],

            'rata2_nominal_per_transaksi': num['rata2_nominal_per_transaksi'],
            'rata2_jumlah_transaksi_per_bulan': num['rata2_jumlah_transaksi_per_bulan'],
            'rata2_nominal_transaksi_per_bulan': num['rata2_nominal_transaksi_per_bulan'],
            'riwayat': num['riwayat'],
            'status_monitoring': num['status_monitoring'],
            'detail': num['detail'],

        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_transaksi_merchant/<data_periode>/<data_nominal>', methods=['GET', ])
def kalkulasi_transaksi_merchant_by_filter(data_periode= None, data_nominal= None):
    data_hasil_hitung = hitung_transaksi_merchant_by_filter(periode= data_periode, nominal= data_nominal)
    dt_htg = []

    for num in data_hasil_hitung:   
        dt_htg.append({
            'st_member': num['st_member'],
            'telp_member': num['telp_member'],
            'nama_member': num['nama_member'],
            'nominal': num['nominal'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],
            'lama_akun_aktif': num['lama_akun_aktif'],

            'rata2_nominal_per_transaksi': num['rata2_nominal_per_transaksi'],
            'rata2_jumlah_transaksi_per_bulan': num['rata2_jumlah_transaksi_per_bulan'],
            'rata2_nominal_transaksi_per_bulan': num['rata2_nominal_transaksi_per_bulan'],
            'riwayat': num['riwayat'],
            'status_monitoring': num['status_monitoring'],
            'detail': num['detail'],

        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/log_transaksi_merchant', methods=['GET', ])
def log_transaksi_merchant():
    data_hasil_hitung = riwayat_log_transaksi_merchant()
    dt_htg = []

    for num in data_hasil_hitung:   
        dt_htg.append({
            'tanggal_dan_waktu': num['tgl_pembayaran'],
            'nama_pengguna': num['nama_member'],
            'id_pengirim': num['kd_member'],
            'nomor_pengguna': num['telp_member'],
            'tanggal_dan_waktu_verifikasi': num['tanggal_dan_waktu_verifikasi'],
            'id_staff_manrisk': num['id_staff_manrisk'],
            'nama_staff_manrisk': num['nama_staff_manrisk'],
            'tanggal_dan_waktu_otorisasi': num['tanggal_dan_waktu_otorisasi'],
            'id_manajer_kepatuhan': num['id_manajer_kepatuhan'],
            'nama_manajer_kepatuhan': num['nama_manajer_kepatuhan'],
            'status': num['status_monitoring'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_ppob', methods=['GET', ])
def kalkulasi_ppob():
    data_hasil_hitung = hitung_ppob()
    dt_htg = []

    for num in data_hasil_hitung:
        dt_htg.append({
            'st_member': num['st_member'],
            'no_telp_member': num['no_telp_member'],
            'nama_member': num['nama_member'],
            'nominal': num['nominal'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],
            'lama_akun_aktif': num['lama_akun_aktif'],
            'rata2_nominal_per_transaksi': num['rata2_nominal_per_transaksi'],
            'rata2_jumlah_transaksi_per_bulan': num['rata2_jumlah_transaksi_per_bulan'],
            'rata2_nominal_transaksi_per_bulan': num['rata2_nominal_transaksi_per_bulan'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],
            'detail': num['detail'],
            'syarat': num['syarat'],
            'riwayat': num['riwayat'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_ppob/<data_periode>/<data_nominal>', methods=['GET', ])
def kalkulasi_ppob_by_filter(data_periode= None, data_nominal= None):
    data_hasil_hitung = hitung_ppob_by_filter(periode= data_periode, nominal= data_nominal)
    dt_htg = []

    for num in data_hasil_hitung:
        dt_htg.append({
            'st_member': num['st_member'],
            'no_telp_member': num['no_telp_member'],
            'nama_member': num['nama_member'],
            'nominal': num['nominal'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],
            'lama_akun_aktif': num['lama_akun_aktif'],

            'rata2_nominal_per_transaksi': num['rata2_nominal_per_transaksi'],
            'rata2_jumlah_transaksi_per_bulan': num['rata2_jumlah_transaksi_per_bulan'],
            'rata2_nominal_transaksi_per_bulan': num['rata2_nominal_transaksi_per_bulan'],

            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],
            'detail': num['detail'],
            'syarat': num['syarat'],
            'riwayat': num['riwayat'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/log_ppob', methods=['GET', ])
def log_ppob():
    data_hasil_hitung = riwayat_log_ppob()
    dt_htg = []

    for num in data_hasil_hitung:
        dt_htg.append({
            'tanggal_dan_waktu': num['tgl_trx'],
            'nama_pengguna': num['nama_member'],
            'id_pengirim': num['kd_member'],
            'nomor_pengguna': num['no_telp_member'],
            'tanggal_dan_waktu_verifikasi': num['tanggal_dan_waktu_verifikasi'],
            'id_staff_manrisk': num['id_staff_manrisk'],
            'nama_staff_manrisk': num['nama_staff_manrisk'],
            'tanggal_dan_waktu_otorisasi': num['tanggal_dan_waktu_otorisasi'],
            'id_manajer_kepatuhan': num['id_manajer_kepatuhan'],
            'nama_manajer_kepatuhan': num['nama_manajer_kepatuhan'],
            'status': num['status_monitoring'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_tarik_dana', methods=['GET', ])
def kalkulasi_tarik_dana():
    data_hasil_hitung = hitung_tarik_dana()
    dt_htg = []

    for num in data_hasil_hitung:
        dt_htg.append({
            'telp_member': num['telp_member'],
            'nama_member': num['nama_member'],
            'nominal': num['nominal'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],

            'lama_akun_aktif': num['lama_akun_aktif'],
            'rata2_nominal_per_transaksi': num['rata2_nominal_per_transaksi'],
            'rata2_jumlah_transaksi_per_bulan': num['rata2_jumlah_transaksi_per_bulan'],
            'rata2_nominal_transaksi_per_bulan': num['rata2_nominal_transaksi_per_bulan'],

            'riwayat': num['riwayat'],
            'status_monitoring': num['status_monitoring'],
            'detail': num['detail'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/kalkulasi_tarik_dana/<data_periode>/<data_nominal>', methods=['GET', ])
def kalkulasi_tarik_dana_by_filter(data_periode= None, data_nominal= None):
    data_hasil_hitung = hitung_tarik_dana_by_filter(periode= data_periode, nominal= data_nominal)
    dt_htg = []

    for num in data_hasil_hitung:
        dt_htg.append({
            'telp_member': num['telp_member'],
            'nama_member': num['nama_member'],
            'nominal': num['nominal'],
            'jumlah_transaksi': num['jumlah_transaksi'],
            'total_nominal': num['total_nominal'],

            'lama_akun_aktif': num['lama_akun_aktif'],
            'rata2_nominal_per_transaksi': num['rata2_nominal_per_transaksi'],
            'rata2_jumlah_transaksi_per_bulan': num['rata2_jumlah_transaksi_per_bulan'],
            'rata2_nominal_transaksi_per_bulan': num['rata2_nominal_transaksi_per_bulan'],

            'riwayat': num['riwayat'],
            'status_monitoring': num['status_monitoring'],
            'detail': num['detail'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)

@blueprint.route('/log_tarik_dana', methods=['GET', ])
def log_tarik_dana():
    data_log_tarik_dana = riwayat_log_tarik_dana()
    dt_htg = []

    for num in data_log_tarik_dana:
        dt_htg.append({
            'tanggal_dan_waktu': num['tgl_tarik'],
            'nama_pengguna': num['nama_member'],
            'id_pengirim': num['kd_member'],
            'nomor_pengguna': num['telp_member'],
            'tanggal_dan_waktu_verifikasi': num['tanggal_dan_waktu_verifikasi'],
            'nama_staff_manrisk': num['nama_staff_manrisk'],
            'tanggal_dan_waktu_otorisasi': num['tanggal_dan_waktu_otorisasi'],
            'id_manajer_kepatuhan': num['id_manajer_kepatuhan'],
            'nama_manajer_kepatuhan': num['nama_manajer_kepatuhan'],
            'status': num['status_monitoring'],
        })
    ret = {'rc': '00', 'rc_desc': 'Sukses', 'data': dt_htg}
    if len(dt_htg)==0:
        return to_client({'rc': '06', 'rc_desc': 'Data user tidak ada'})
    return to_client(ret)