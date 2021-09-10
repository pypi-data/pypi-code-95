# -*- coding: utf-8 -*-

"""CCXT: CryptoCurrency eXchange Trading Library"""

# MIT License
# Copyright (c) 2017 Igor Kroitor
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ----------------------------------------------------------------------------

__version__ = '1.56.19'

# ----------------------------------------------------------------------------

from ccxt_1_56_19.base.exchange import Exchange                     # noqa: F401
from ccxt_1_56_19.base.precise import Precise                       # noqa: F401

from ccxt_1_56_19.base.decimal_to_precision import decimal_to_precision  # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import TRUNCATE              # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import ROUND                 # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import DECIMAL_PLACES        # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import SIGNIFICANT_DIGITS    # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import TICK_SIZE             # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import NO_PADDING            # noqa: F401
from ccxt_1_56_19.base.decimal_to_precision import PAD_WITH_ZERO         # noqa: F401

from ccxt_1_56_19.base import errors
from ccxt_1_56_19.base.errors import BaseError                      # noqa: F401
from ccxt_1_56_19.base.errors import ExchangeError                  # noqa: F401
from ccxt_1_56_19.base.errors import AuthenticationError            # noqa: F401
from ccxt_1_56_19.base.errors import PermissionDenied               # noqa: F401
from ccxt_1_56_19.base.errors import AccountSuspended               # noqa: F401
from ccxt_1_56_19.base.errors import ArgumentsRequired              # noqa: F401
from ccxt_1_56_19.base.errors import BadRequest                     # noqa: F401
from ccxt_1_56_19.base.errors import BadSymbol                      # noqa: F401
from ccxt_1_56_19.base.errors import BadResponse                    # noqa: F401
from ccxt_1_56_19.base.errors import NullResponse                   # noqa: F401
from ccxt_1_56_19.base.errors import InsufficientFunds              # noqa: F401
from ccxt_1_56_19.base.errors import InvalidAddress                 # noqa: F401
from ccxt_1_56_19.base.errors import AddressPending                 # noqa: F401
from ccxt_1_56_19.base.errors import InvalidOrder                   # noqa: F401
from ccxt_1_56_19.base.errors import OrderNotFound                  # noqa: F401
from ccxt_1_56_19.base.errors import OrderNotCached                 # noqa: F401
from ccxt_1_56_19.base.errors import CancelPending                  # noqa: F401
from ccxt_1_56_19.base.errors import OrderImmediatelyFillable       # noqa: F401
from ccxt_1_56_19.base.errors import OrderNotFillable               # noqa: F401
from ccxt_1_56_19.base.errors import DuplicateOrderId               # noqa: F401
from ccxt_1_56_19.base.errors import NotSupported                   # noqa: F401
from ccxt_1_56_19.base.errors import NetworkError                   # noqa: F401
from ccxt_1_56_19.base.errors import DDoSProtection                 # noqa: F401
from ccxt_1_56_19.base.errors import RateLimitExceeded              # noqa: F401
from ccxt_1_56_19.base.errors import ExchangeNotAvailable           # noqa: F401
from ccxt_1_56_19.base.errors import OnMaintenance                  # noqa: F401
from ccxt_1_56_19.base.errors import InvalidNonce                   # noqa: F401
from ccxt_1_56_19.base.errors import RequestTimeout                 # noqa: F401
from ccxt_1_56_19.base.errors import error_hierarchy                # noqa: F401

from ccxt_1_56_19.aax import aax                                    # noqa: F401
from ccxt_1_56_19.aofex import aofex                                # noqa: F401
from ccxt_1_56_19.ascendex import ascendex                          # noqa: F401
from ccxt_1_56_19.bequant import bequant                            # noqa: F401
from ccxt_1_56_19.bibox import bibox                                # noqa: F401
from ccxt_1_56_19.bigone import bigone                              # noqa: F401
from ccxt_1_56_19.binance import binance                            # noqa: F401
from ccxt_1_56_19.binancecoinm import binancecoinm                  # noqa: F401
from ccxt_1_56_19.binanceus import binanceus                        # noqa: F401
from ccxt_1_56_19.binanceusdm import binanceusdm                    # noqa: F401
from ccxt_1_56_19.bit2c import bit2c                                # noqa: F401
from ccxt_1_56_19.bitbank import bitbank                            # noqa: F401
from ccxt_1_56_19.bitbay import bitbay                              # noqa: F401
from ccxt_1_56_19.bitbns import bitbns                              # noqa: F401
from ccxt_1_56_19.bitcoincom import bitcoincom                      # noqa: F401
from ccxt_1_56_19.bitfinex import bitfinex                          # noqa: F401
from ccxt_1_56_19.bitfinex2 import bitfinex2                        # noqa: F401
from ccxt_1_56_19.bitflyer import bitflyer                          # noqa: F401
from ccxt_1_56_19.bitforex import bitforex                          # noqa: F401
from ccxt_1_56_19.bitget import bitget                              # noqa: F401
from ccxt_1_56_19.bithumb import bithumb                            # noqa: F401
from ccxt_1_56_19.bitmart import bitmart                            # noqa: F401
from ccxt_1_56_19.bitmex import bitmex                              # noqa: F401
from ccxt_1_56_19.bitpanda import bitpanda                          # noqa: F401
from ccxt_1_56_19.bitso import bitso                                # noqa: F401
from ccxt_1_56_19.bitstamp import bitstamp                          # noqa: F401
from ccxt_1_56_19.bitstamp1 import bitstamp1                        # noqa: F401
from ccxt_1_56_19.bittrex import bittrex                            # noqa: F401
from ccxt_1_56_19.bitvavo import bitvavo                            # noqa: F401
from ccxt_1_56_19.bitz import bitz                                  # noqa: F401
from ccxt_1_56_19.bl3p import bl3p                                  # noqa: F401
from ccxt_1_56_19.braziliex import braziliex                        # noqa: F401
from ccxt_1_56_19.btcalpha import btcalpha                          # noqa: F401
from ccxt_1_56_19.btcbox import btcbox                              # noqa: F401
from ccxt_1_56_19.btcmarkets import btcmarkets                      # noqa: F401
from ccxt_1_56_19.btctradeua import btctradeua                      # noqa: F401
from ccxt_1_56_19.btcturk import btcturk                            # noqa: F401
from ccxt_1_56_19.buda import buda                                  # noqa: F401
from ccxt_1_56_19.bw import bw                                      # noqa: F401
from ccxt_1_56_19.bybit import bybit                                # noqa: F401
from ccxt_1_56_19.cdax import cdax                                  # noqa: F401
from ccxt_1_56_19.cex import cex                                    # noqa: F401
from ccxt_1_56_19.coinbase import coinbase                          # noqa: F401
from ccxt_1_56_19.coinbaseprime import coinbaseprime                # noqa: F401
from ccxt_1_56_19.coinbasepro import coinbasepro                    # noqa: F401
from ccxt_1_56_19.coincheck import coincheck                        # noqa: F401
from ccxt_1_56_19.coinegg import coinegg                            # noqa: F401
from ccxt_1_56_19.coinex import coinex                              # noqa: F401
from ccxt_1_56_19.coinfalcon import coinfalcon                      # noqa: F401
from ccxt_1_56_19.coinfloor import coinfloor                        # noqa: F401
from ccxt_1_56_19.coinmarketcap import coinmarketcap                # noqa: F401
from ccxt_1_56_19.coinmate import coinmate                          # noqa: F401
from ccxt_1_56_19.coinone import coinone                            # noqa: F401
from ccxt_1_56_19.coinspot import coinspot                          # noqa: F401
from ccxt_1_56_19.crex24 import crex24                              # noqa: F401
from ccxt_1_56_19.currencycom import currencycom                    # noqa: F401
from ccxt_1_56_19.delta import delta                                # noqa: F401
from ccxt_1_56_19.deribit import deribit                            # noqa: F401
from ccxt_1_56_19.digifinex import digifinex                        # noqa: F401
from ccxt_1_56_19.eqonex import eqonex                              # noqa: F401
from ccxt_1_56_19.equos import equos                                # noqa: F401
from ccxt_1_56_19.exmo import exmo                                  # noqa: F401
from ccxt_1_56_19.exx import exx                                    # noqa: F401
from ccxt_1_56_19.flowbtc import flowbtc                            # noqa: F401
from ccxt_1_56_19.ftx import ftx                                    # noqa: F401
from ccxt_1_56_19.gateio import gateio                              # noqa: F401
from ccxt_1_56_19.gemini import gemini                              # noqa: F401
from ccxt_1_56_19.hbtc import hbtc                                  # noqa: F401
from ccxt_1_56_19.hitbtc import hitbtc                              # noqa: F401
from ccxt_1_56_19.hollaex import hollaex                            # noqa: F401
from ccxt_1_56_19.huobi import huobi                                # noqa: F401
from ccxt_1_56_19.huobijp import huobijp                            # noqa: F401
from ccxt_1_56_19.huobipro import huobipro                          # noqa: F401
from ccxt_1_56_19.idex import idex                                  # noqa: F401
from ccxt_1_56_19.independentreserve import independentreserve      # noqa: F401
from ccxt_1_56_19.indodax import indodax                            # noqa: F401
from ccxt_1_56_19.itbit import itbit                                # noqa: F401
from ccxt_1_56_19.kraken import kraken                              # noqa: F401
from ccxt_1_56_19.kucoin import kucoin                              # noqa: F401
from ccxt_1_56_19.kuna import kuna                                  # noqa: F401
from ccxt_1_56_19.latoken import latoken                            # noqa: F401
from ccxt_1_56_19.lbank import lbank                                # noqa: F401
from ccxt_1_56_19.liquid import liquid                              # noqa: F401
from ccxt_1_56_19.luno import luno                                  # noqa: F401
from ccxt_1_56_19.lykke import lykke                                # noqa: F401
from ccxt_1_56_19.mercado import mercado                            # noqa: F401
from ccxt_1_56_19.mixcoins import mixcoins                          # noqa: F401
from ccxt_1_56_19.ndax import ndax                                  # noqa: F401
from ccxt_1_56_19.novadax import novadax                            # noqa: F401
from ccxt_1_56_19.oceanex import oceanex                            # noqa: F401
from ccxt_1_56_19.okcoin import okcoin                              # noqa: F401
from ccxt_1_56_19.okex import okex                                  # noqa: F401
from ccxt_1_56_19.okex3 import okex3                                # noqa: F401
from ccxt_1_56_19.okex5 import okex5                                # noqa: F401
from ccxt_1_56_19.paymium import paymium                            # noqa: F401
from ccxt_1_56_19.phemex import phemex                              # noqa: F401
from ccxt_1_56_19.poloniex import poloniex                          # noqa: F401
from ccxt_1_56_19.probit import probit                              # noqa: F401
from ccxt_1_56_19.qtrade import qtrade                              # noqa: F401
from ccxt_1_56_19.ripio import ripio                                # noqa: F401
from ccxt_1_56_19.stex import stex                                  # noqa: F401
from ccxt_1_56_19.therock import therock                            # noqa: F401
from ccxt_1_56_19.tidebit import tidebit                            # noqa: F401
from ccxt_1_56_19.tidex import tidex                                # noqa: F401
from ccxt_1_56_19.timex import timex                                # noqa: F401
from ccxt_1_56_19.upbit import upbit                                # noqa: F401
from ccxt_1_56_19.vcc import vcc                                    # noqa: F401
from ccxt_1_56_19.wavesexchange import wavesexchange                # noqa: F401
from ccxt_1_56_19.whitebit import whitebit                          # noqa: F401
from ccxt_1_56_19.xena import xena                                  # noqa: F401
from ccxt_1_56_19.yobit import yobit                                # noqa: F401
from ccxt_1_56_19.zaif import zaif                                  # noqa: F401
from ccxt_1_56_19.zb import zb                                      # noqa: F401

exchanges = [
    'aax',
    'aofex',
    'ascendex',
    'bequant',
    'bibox',
    'bigone',
    'binance',
    'binancecoinm',
    'binanceus',
    'binanceusdm',
    'bit2c',
    'bitbank',
    'bitbay',
    'bitbns',
    'bitcoincom',
    'bitfinex',
    'bitfinex2',
    'bitflyer',
    'bitforex',
    'bitget',
    'bithumb',
    'bitmart',
    'bitmex',
    'bitpanda',
    'bitso',
    'bitstamp',
    'bitstamp1',
    'bittrex',
    'bitvavo',
    'bitz',
    'bl3p',
    'braziliex',
    'btcalpha',
    'btcbox',
    'btcmarkets',
    'btctradeua',
    'btcturk',
    'buda',
    'bw',
    'bybit',
    'cdax',
    'cex',
    'coinbase',
    'coinbaseprime',
    'coinbasepro',
    'coincheck',
    'coinegg',
    'coinex',
    'coinfalcon',
    'coinfloor',
    'coinmarketcap',
    'coinmate',
    'coinone',
    'coinspot',
    'crex24',
    'currencycom',
    'delta',
    'deribit',
    'digifinex',
    'eqonex',
    'equos',
    'exmo',
    'exx',
    'flowbtc',
    'ftx',
    'gateio',
    'gemini',
    'hbtc',
    'hitbtc',
    'hollaex',
    'huobi',
    'huobijp',
    'huobipro',
    'idex',
    'independentreserve',
    'indodax',
    'itbit',
    'kraken',
    'kucoin',
    'kuna',
    'latoken',
    'lbank',
    'liquid',
    'luno',
    'lykke',
    'mercado',
    'mixcoins',
    'ndax',
    'novadax',
    'oceanex',
    'okcoin',
    'okex',
    'okex3',
    'okex5',
    'paymium',
    'phemex',
    'poloniex',
    'probit',
    'qtrade',
    'ripio',
    'stex',
    'therock',
    'tidebit',
    'tidex',
    'timex',
    'upbit',
    'vcc',
    'wavesexchange',
    'whitebit',
    'xena',
    'yobit',
    'zaif',
    'zb',
]

base = [
    'Exchange',
    'Precise',
    'exchanges',
    'decimal_to_precision',
]

__all__ = base + errors.__all__ + exchanges
