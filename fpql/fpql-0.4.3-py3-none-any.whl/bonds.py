from QuantLib.QuantLib import OptionletVolatilityStructureHandle
from fpql.termstructure import qlFlatForward, qlPiecewise
import QuantLib as ql 
from .pymodels import *
from .ql_utils import *
from .ql_conventions import *
from .ql_enums import *
from . import pricingmodels as pm


def get_qlfixedratebond(bond_info: FixedRateBond, setting: BondSetting,
                calendar):
    
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    schedule = ql.Schedule(datestr_to_qldate(bond_info.issue_date), 
                            datestr_to_qldate(bond_info.maturity), 
                            ql_period, 
                            calendar, 
                            ql_business_day[setting.business_day],
                            ql_business_day[setting.terminate_business_day],
                            ql_date_generation[setting.date_gen],
                            setting.is_eom)
    qlbond = ql.FixedRateBond(setting.start_basis, 
                                bond_info.face_value, 
                                schedule, [bond_info.coupon/100], 
                                ql_day_count[setting.day_count])
    return qlbond


def get_qlbond(bond_info: FixedRateBond, setting: BondSetting,
                calendar):
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    day_count = ql_day_count[setting.day_count]
    schedule = ql.Schedule(datestr_to_qldate(bond_info.issue_date), 
                            datestr_to_qldate(bond_info.maturity), 
                            ql_period, 
                            calendar, 
                            ql_business_day[setting.business_day],
                            ql_business_day[setting.terminate_business_day],
                            ql_date_generation[setting.date_gen],
                            setting.is_eom)

    interest = ql.FixedRateLeg(schedule, 
                                day_count, 
                                [100.], 
                                [bond_info.coupon/100])
    qlbond = ql.Bond(0, ql.TARGET(), 
                    datestr_to_qldate(bond_info.issue_date), 
                    interest)
    
    return qlbond
    

def calc_fixbond_structures(value_date: str, 
                            bond_info: FixedRateBond, 
                            setting: BondSetting,
                            calendar):
    #create Schedule
    ql_period = ql.Period(ql_freq_tenor[setting.frequency])
    schedule = ql.Schedule(datestr_to_qldate(bond_info.issue_date), 
                            datestr_to_qldate(bond_info.maturity), 
                            ql_period, 
                            calendar, 
                            ql_business_day[setting.business_day],
                            ql_business_day[setting.terminate_business_day],
                            ql_date_generation[setting.date_gen],
                            setting.is_eom)
    
    # a sequence of QuantLib.QuantLib.SimpleCashFlow
    interests = ql.FixedRateLeg(schedule, 
                            ql_day_count[setting.day_count],
                            [bond_info.face_value], 
                            [bond_info.coupon/100],
                            ql.Following)
    no_of_interests = len(interests)
    schedule = list(schedule)
    no_of_dates = len(schedule)
    startdates = schedule[:no_of_dates - 1]
    enddates = schedule[1: no_of_dates]
    structures = []
    for i in range(no_of_interests):
        fv_flow = 0
        if i == no_of_interests - 1:
            cashflow = bond_info.face_value + interests[i].amount()
            fv_flow = bond_info.face_value
        else :
            cashflow = interests[i].amount()
    
        thestructure = {"start_date": startdates[i].ISO(),
                        "end_date": enddates[i].ISO(),
                        "payment_date": interests[i].date().ISO(),
                        "face_value": bond_info.face_value,
                        "coupon": bond_info.coupon,
                        "face_value_flow": fv_flow,
                        "interest": interests[i].amount(),
                        "cashflow": cashflow} 
        
        structure = Structure(**thestructure)  
        structures.append(structure)  
    
    return structures


def fixbond_ytm(clean_price: float, 
                daycount: DayCount,
                frequency: Frequency,
                thebond: ql.QuantLib.Bond):
    
    day_count = ql_day_count[daycount]
    freq = ql_frequency[frequency]
    ytm = thebond.bondYield(clean_price, 
                                day_count,
                                ql.Compounded,
                                freq)
    return ytm * 100


def bond_functions_cashflows(qlvaluedate:ql.QuantLib.Date, 
                            qlbond: ql.QuantLib.FixedRateBond):
    previous_cashflow_date = ql.BondFunctions.previousCashFlowDate(qlbond, qlvaluedate)
    previous_cashflow_amount = ql.BondFunctions.previousCashFlowAmount(qlbond, qlvaluedate)
    next_cashflow_date = ql.BondFunctions.nextCashFlowDate(qlbond, qlvaluedate)
    next_cashflow_amount = ql.BondFunctions.nextCashFlowAmount(qlbond, qlvaluedate)
    cf_info = {"previous_cashflow_date": previous_cashflow_date,
                "previous_cashflow_amount": previous_cashflow_amount,
                "next_cashflow_date": next_cashflow_date,
                "next_cashflow_amount": next_cashflow_amount}
    cfi = CashFlowInspector(**cf_info)
    return cfi


def bond_functions_coupons(qlbond: ql.QuantLib.FixedRateBond):
    previous_coupon_rate = ql.BondFunctions.previousCouponRate(qlbond)
    next_coupon_rate = ql.BondFunctions.nextCouponRate(qlbond)
    accrual_start_date = ql.BondFunctions.accrualStartDate(qlbond).ISO()
    accrual_end_date = ql.BondFunctions.accrualEndDate(qlbond)
    accrual_period = ql.BondFunctions.accrualPeriod(qlbond)
    accrual_days = ql.BondFunctions.accrualDays(qlbond)
    accrued_period = ql.BondFunctions.accruedPeriod(qlbond)
    accrued_days = ql.BondFunctions.accruedDays(qlbond)
    accrued_amount = ql.BondFunctions.accruedAmount(qlbond)

    c_info = {"previous_coupon_rate": previous_coupon_rate,
                "next_coupon_rate": next_coupon_rate, 
                "accrual_start_date": accrual_start_date,
                "accrual_end_date": accrual_end_date,
                "accrual_period": accrual_period,
                "accrual_days": accrual_days,
                "accrued_period": accrued_period,
                "accrued_days": accrued_days,
                "accrued_amount": accrued_amount}
    ci = CashFlowInspector(**c_info)

    return ci


def bond_functions_risks(qlbond: ql.QuantLib.FixedRateBond,
                        i_rate: ql.QuantLib.InterestRate):
    accrued = ql.BondFunctions.accruedAmount(qlbond)
    accrued_period = ql.BondFunctions.accruedPeriod(qlbond)
    clean_price = ql.BondFunctions.cleanPrice(qlbond, i_rate)
    bps = ql.BondFunctions.bps(qlbond, i_rate)
    duration = ql.BondFunctions.duration(qlbond, i_rate, ql.Duration.Macaulay)
    modified_duration = ql.BondFunctions.duration(qlbond, i_rate, ql.Duration.Modified)
    convexity = ql.BondFunctions.convexity(qlbond, i_rate)
    basis_point_value = ql.BondFunctions.basisPointValue(qlbond, i_rate)
    yield_value_basis_point = ql.BondFunctions.yieldValueBasisPoint(qlbond, i_rate)
    stats = {"accrued": accrued,
            "accrued_period": accrued_period,
            "clean_price": clean_price,
            "bps": bps,
            "duration": duration,
            "modified_duration": modified_duration,
            "convexity": convexity,
            "basis_point_value": basis_point_value,
            "yield_value_basis_point": yield_value_basis_point}
    risks = BondRisk(**stats)
    return risks


def z_spread(clean_price: float,
            fixbond:ql.QuantLib.FixedRateBond, 
            yieldcurve: ql.QuantLib.TermStructure,
            setting: BondSetting):
    return ql.BondFunctions.zSpread(fixbond, 
            clean_price, yieldcurve, 
            ql_day_count[setting.day_count], 
            ql.Compounded, 
            ql_frequency[setting.frequency])


def get_call_schedule(call_prices: List[CallabilityPrice]):
    callability_schedule = ql.CallabilitySchedule()

    for call_price in call_prices:
        c_price  = ql.CallabilityPrice(call_price.price, call_price.price_type)
        calldate = datestr_to_qldate(call_price.date)
        callability_schedule.append(ql.Callability(c_price, 
                                                    call_price.option_type,
                                                    calldate)
                                    )
    return callability_schedule


def get_qlcallablebond(bond_info: FixedRateBond,
                        bond_schedule: ql.QuantLib.Schedule,
                        coupons: List[float],
                        call_schedule: ql.QuantLib.CallabilitySchedule,
                        settlement_days: int = 0):
    
    callbond = ql.CallableFixedRateBond(
                settlement_days, 
                bond_info.face_value,
                bond_schedule, 
                coupons, 
                ql_day_count[bond_info.settings.day_count],
                ql_business_day[bond_info.settings.business_day], 
                bond_info.face_value, 
                datestr_to_qldate(bond_info.issue_date),
                call_schedule)
    return callbond


def callbond_stats(**params):
                    #clean_price: float,
                    #engine: ql.QuantLib.TreeCallableFixedRateBondEngine,
                    #curve: Optional[ql.QuantLib.YieldTermStructureHandle] = None):
    
    vdate = datestr_to_qldate(params.get('value_date'))
    call_class = params.get('callable_bond_param')
    ql_calendar = params.get('qlcalendar')
    ql_callbond = qlCallableBond_from_Class(call_class, ql_calendar)

    if params.get("curve"):
        curve_handle = params['curve']
    else:
        if call_class.use_flat_curve:
            if call_class.flat_curve:
                ffwd = qlFlatForward(call_class.flat_curve)
                curve_handle = ql.YieldTermStructureHandle(ffwd)
        else:
            pwc = qlPiecewise(call_class.piecewise_curve, ql_calendar)
            curve_handle = ql.YieldTermStructureHandle(pwc)
    
    engine = params.get('engine')
    if engine:
        ql_callbond.setPricingEngine(engine)
    else:
        return {}
    
    call_risks = {}
    
    if params.get('clean_price'):
        c_price = params['clean_price']
    else:
        c_price = ql_callbond.cleanPrice()
        call_risks['Clean Price'] = c_price
    oas = None

    try:
        oas = ql_callbond.OAS(c_price, 
                            curve_handle,
                            ql_day_count[call_class.info.settings.day_count],
                            ql.Compounded,
                            ql_frequency[call_class.info.settings.frequency],
                            vdate) * 100
        call_risks["OAS"] =  oas
        
    except:
        pass

    
    bond_yield  = ql_callbond.bondYield(c_price,
                        ql_day_count[call_class.info.settings.day_count],
                        ql.Compounded,
                        ql_frequency[call_class.info.settings.frequency],
                        vdate) * 100
    call_risks["Yield"] = bond_yield
    
    #OAS/Spread is not supported for trees other than OneFactorModel
    if oas is not None:
        e_convex = ql_callbond.effectiveConvexity(oas/100, 
                                    curve_handle,
                                    ql_day_count[call_class.info.settings.day_count],
                                    ql.Compounded,
                                    ql_frequency[call_class.info.settings.frequency])
        call_risks["Effective Convexity"] = e_convex

        e_duration = ql_callbond.effectiveDuration(oas/100, 
                                curve_handle,
                                ql_day_count[call_class.info.settings.day_count],
                                ql.Compounded,
                                ql_frequency[call_class.info.settings.frequency])
        call_risks["Effective Duration"] = e_duration


    return call_risks


def qlCallableBond_from_Class(call_class: CallableBondParam,
                            qlcalendar):
    qlschedule = qlSchedule_from_Model(call_class.info, qlcalendar) 
    structure = structure_from_qlSchedule(call_class.info,
                                            qlschedule)
    call_class.structure = structure
    qlcall_schedule = qlCallabilitySchedule_from_class(call_class.call_structure)
    qlcallbond = get_qlcallablebond(call_class.info, 
                                    qlschedule, 
                                    [call_class.info.coupon/100], 
                                    qlcall_schedule )
    
    return qlcallbond

        