from typing import List, Optional
from .pymodels import *
from .ql_conventions import *
import QuantLib as ql


def create_calendar(description: Optional[str], 
                    holidays:List[Holiday] = [], 
                    mycal = None):

    cal = ql.BespokeCalendar(description)
    qldates = [datestr_to_qldate(holiday.date) for holiday in holidays]
    for qldate in qldates:
        cal.addHoliday(qldate)
    
    if not mycal:
        calendar = ql.JointCalendar(cal, ql.WeekendsOnly())
    else:
        calendar = ql.JointCalendar(cal, mycal)
    
    return calendar
    

def datestr_to_qldate(datestr):
    vdate = datestr.split("-")
    vdt = [int(vdat) for vdat in vdate]
    return ql.Date(vdt[2], vdt[1], vdt[0])


def qlSchedule_from_Model(info: FixedRateBond, 
                        ql_calendar):
    return qlSchedule(info.issue_date,
                        info.maturity,
                        ql.Period(ql_frequency[info.settings.frequency]), 
                        ql_calendar, 
                        info.settings.business_day, 
                        info.settings.business_day, 
                        info.settings.date_gen, 
                        info.settings.is_eom)


def structure_from_qlSchedule(bond_info: FixedRateBond,
                            schedule: ql.QuantLib.Schedule):
    interests = ql.FixedRateLeg(schedule, 
                            ql_day_count[bond_info.settings.day_count],
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
        if i == no_of_interests - 1:
            cashflow = bond_info.face_value + interests[i].amount()
        else :
            cashflow = interests[i].amount()
        thestructure = {"start_date": startdates[i].ISO(),
                        "end_date": enddates[i].ISO(),
                        "payment_date": interests[i].date().ISO(),
                        "face_value": bond_info.face_value,
                        "coupon": bond_info.coupon,
                        "face_value_flow": bond_info.face_value,
                        "interest": interests[i].amount(),
                        "cashflow": cashflow} 
        
        structure = Structure(**thestructure)  
        structures.append(structure)  
    return structures


def qlSchedule_from_Structure(structures: List[Structure]):

    dates = []
    dates.append(structures[0].start_date)
    for structure in structures:
        dates.append(structure.end_date)
    #print(dates)
    qlschedule = ql.Schedule([datestr_to_qldate(dt) for dt in dates])
    return qlschedule


def qlDividendSchedule_from_CashFLows(cashflows: List[CashFlow]):
    schedule = ql.DividendSchedule([ ql.SimpleCashFlow(cf.amount, datestr_to_qldate(cf.date)) for cf in cashflows])
    return schedule


def get_qlPeriod(tenor:str):
    prd = tenor[-1]
    number = int(tenor[:len(tenor)-1])
    return  ql.Period(number, ql_tenor[prd])


def qlSchedule(issue_date: str, 
            maturity: str, 
            period: ql.QuantLib.Period, 
            ql_calendar,
            business_day: BusinessDay, 
            maturity_business_day: BusinessDay,
            date_gen: DateGeneration, 
            eom: bool = False):
    """
    Creates list of dates. 

        Parameters:
            issue_date (str): if date_gen is DateGeneration.backward, issue_date can 
                be treated as the value date, otherwise please use issue date for 
                accurate dates.
            maturity (str): maturity of the instrument.
            frequency (str): frequency of coupon payment
            ql_calendar: ql.Calendar relevant for the currency.
            business_day (str): business day convention for the dates.
            maturity_business_day (str): business day convention for the 
                maturity of the instrument
            date_gen (str): manner in which dates are generated.
            eom (bool): if the start date is at the end of the month, whether 
                other dates are required to be scheduled at the end of the month
                (except the last date).

        Returns:
            list of ql.Dates()
    """
    vdate = datestr_to_qldate(issue_date)
    mdate = datestr_to_qldate(maturity)
    
    schedule = ql.Schedule(vdate, 
                mdate, 
                period, 
                ql_calendar, 
                ql_business_day[business_day],
                ql_business_day[maturity_business_day], 
                ql_date_generation[date_gen], 
                eom)
    return schedule


def qlSchedule2(thebond: FixedRateBond,
            ql_calendar):
    
    vdate = datestr_to_qldate(thebond.issue_date)
    mdate = datestr_to_qldate(thebond.maturity)
    
    schedule = ql.Schedule(vdate, 
                mdate, 
                ql.Period(ql_frequency[thebond.settings.frequency]), 
                ql_calendar, 
                ql_business_day[thebond.settings.business_day],
                ql_business_day[thebond.settings.terminate_business_day], 
                ql_date_generation[thebond.settings.date_gen], 
                thebond.settings.is_eom)
    return schedule


def qlMakeScedule(issue_date: str, maturity: str, frequency:str, ql_calendar = None,
                business_day: Optional[BusinessDay] = None, 
                maturity_business_day: Optional[BusinessDay] = None,
                date_gen: Optional[DateGeneration] = None, eom: bool = False):

    vdate = datestr_to_qldate(issue_date)
    mdate = datestr_to_qldate(maturity)
    freq = ql.Period(frequency)
    if business_day:
        ql_bus_day = ql_business_day[business_day]
    if maturity_business_day:
        ql_mat_bus_day = ql_business_day[maturity_business_day]
    if date_gen:
        ql_date_gen = ql_date_generation[date_gen]
    schedule = ql.MakeSchedule(vdate, mdate, freq)
    return schedule


def qlCallabilitySchedule_from_class(call_schedule: List[CallabilityPrice]):
    callability_schedule = ql.CallabilitySchedule()
    
    for calldata in call_schedule:
        call_price  = ql.CallabilityPrice(calldata.price, 
                                            calldata.price_type)
        call_date = datestr_to_qldate(calldata.date)
        callability = ql.Callability(call_price, 
                                calldata.option_type,
                                call_date)
        callability_schedule.append(callability)
    return callability_schedule
