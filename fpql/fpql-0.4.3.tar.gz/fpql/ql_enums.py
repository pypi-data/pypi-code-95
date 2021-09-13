from pydantic import BaseModel, validator
from typing import List
from enum import Enum


class StartBasis(int, Enum):
    spot = 2
    tom = 1
    today = 0


class BusinessDay(str, Enum):
    no_adjustment = "No Adjustment" 
    following = "Following" 
    mod_following = "Modified Following"
    preceding = "Preceding"
    mod_preceding = "Modified Preceding"


class DayCount(str, Enum):
    act_365_fixed = 'Actual/365 Fixed' 
    act_365_fixed_canadian = 'Actual/365 Fixed (Canadian)'
    act_365_fixed_noleap = 'Actual/365 Fixed (No Leap)'
    act_360 = 'Actual/360'
    act_act = 'Actual/Actual'
    act_act_isma = 'Actual/Actual (ISMA)'
    act_act_bond = 'Actual/Actual (Bond)'
    act_act_isda = 'Actual/Actual (ISDA)'
    act_act_historical = 'Actual/Actual (Historical)'
    act_act_act365 ='Actual/Actual (Actual365)'
    act_act_afb = 'Actual/Actual (AFB)'
    business252 = 'Business252'
    thirty360 = 'Thirty360'


class DateGeneration(str, Enum):
    forward = "Forward from issue date"
    backward = "Backward from maturity date"
    zero = "Zero"
    third_wednesday = "ThirdWednesday"
    twentieth = "Twentieth"
    twentieth_IMM = "TwentiethIMM"
    cds = "CDS"


class Frequency(str, Enum):
    no_frequency = "No Frequency"
    once = "Once"
    annual = "Annual" 
    semi_annual = "Semi-Annual"
    every_four_months = "Every Four Months"
    quarterly = "Quarterly"
    bi_monthly = "Bi-Monthly"
    monthly = "Monthly"
    every_fourth_week = "Every Fourth Week"
    bi_weekly = "Bi-Weekly"
    weekly = "Weekly"
    daily = "Daily"


class Country(str, Enum):
    argentina = "Argentina"
    brazil = "Brazil"
    canada = "Canada"
    china = "China"
    czechRepublic  = "Czech Republic" 
    france = "France" 
    germany = "Germany" 
    hongkong = "Hong Kong"
    iceland = "Iceland"
    india = "India" 
    indonesia = "Indonesia" 
    israel = "Israel"
    italy = "Italy"
    mexico = "Mexico"
    russia = "Russia"
    saudiarabia = "Saudi Arabia"
    singapore = "Singapore"
    slovakia = "Slovakia"
    southkorea = "South Korea"
    taiwan = "Taiwan"
    ukraine = "Ukraine" 
    unitedkingdom = "United Kingdom" 
    unitedstates = "United States"
    target = "TARGET"


class PiecewiseMethods(str, Enum):
    logcubicdiscount = "LogCubicDiscount"
    loglineardiscount = "LogLinearDiscount"
    linearzero = "LinearZero"
    cubiczero = "CubicZero"
    linearforward = "LinearForward"
    splinecubicdiscount = "SplineCubicDiscount"


class ZeroCurveMethods(str, Enum):
    zerocurve = "ZeroCurve"
    loglinearZeroCurve = "LogLinearZeroCurve"
    cubiczerocurve = "CubicZeroCurve"
    naturalcubiczerocurve = "NaturalCubicZeroCurve"
    logcubiczerocurve = "LogCubicZeroCurve"
    monotoniccubiczerocurve = "MonotonicCubicZeroCurve"


class Compounding(str, Enum):
    simple = "Simple"
    compounded = "Compounded"
    continuous = "Continuous"
    simplethencontinuous = "SimpleThenCompounded"
    compoundedthensimple = "CompoundedThenSimple"


class ShortRateModel(str, Enum):
    vasicek = 'Vasicek'
    blackkarasinski = 'BlackKarasinski'
    hullwhite = 'HullWhite'
    gsr = "gsr"
    g2 = 'g2'


class BondPriceType(int, Enum):
    dirty = 0
    clean = 1


class OptionType(int,Enum):
    calloption = 0
    putoption = 1


class OptionExercise(str, Enum):
    american = "American"
    european = "European"
    bermudan = "Bermudan"

class GeneralisedBlackScholes(str, Enum):
    black_scholes = "Black Scholes"
    black_scholes_merton = "Black Scholes Merton"
    generalized_black_scholes  = "Generalized Black Scholes"
    black = "Black"
    garmankohlagen = "Garman Kohlagen"

    
class StochasticProcess(str, Enum):
    geometric_brownian_motion = "Geometric Brownian Motion"
    black_scholes = "Black Scholes"
    black_scholes_merton = "Black Scholes Merton"
    generalized_black_scholes  = "Generalized Black Scholes"
    extended_ornstein_uhlenbeck = 'Extended Ornstein Uhlenbeck'
    ext_OU_with_jumps = "Ext OU With Jumps"
    black = "Black"
    merton76 = "Merton76"
    variance_gamma = "Variance Gamma"
    garmankohlagen = "Garman Kohlagen"
    heston = "Heston"
    hestonSLV = "HestonSLV"
    hull_white = "Hull White"
    hull_white_forward = "Hull White Forward"
    gsr = "GSR"


class VolatilityModel(str, Enum):
    black_constant_vol = "Black Constant Vol"
    black_variance_curve = "Black Variance Curve"
    black_variance_surface = "Black Variance Surface"
    heston_black_vol_surface = "Heston Black Vol Surface"
    andreasen_huge_volatility_adapter = "Andreasen Huge Volatility Adapter"
    andreasen_huge_local_vol_adapter = "Andreasen Huge Local Vol Adapter"
    local_constant_vol = "Local Constant Vol"
    local_vol_surface = "Local Vol Surface"