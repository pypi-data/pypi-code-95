import QuantLib as ql
from . import pymodels, ql_enums as qle, ql_utils as qlu, ql_conventions as qlc


class FixedBondVal:
    def __init__(self):
        pass

    @property
    def bond_info(self):
        return self.__bond_info

    @bond_info.setter
    def bond_info(self, bond_info):
        self.__bond_info = bond_info
        

class ConvertibleFixedRateBond:
    def __init__(self, thebond: pymodels.ConvertibleFixedRate, qlcalendar):
        self.__convbond = thebond
        self.__engine = None
        self.__qlcalendar = qlcalendar
    
    @property
    def engine(self):
        return self.__engine

    @engine.setter
    def engine(self, engine):
        self.__engine = engine


    @property
    def thebond(self):
        return self.__convbond
    

    @property
    def qlcalendar(self):
        return self.__qlcalendar

    @qlcalendar.setter
    def engine(self, qlcalendar):
        self.qlcalendar = qlcalendar



    def qlconvertible(self, value_date:str):
        exercise = self.__exercise(value_date)
        dividend_schedule = self.__dividend_schedule_from_dividend_structure()
        callability_schedule = self.__call_schedule_from_option_schedules()
        credit_spread_handle = ql.QuoteHandle(ql.SimpleQuote(self.__convbond.credit_spread/100))
        #print(self.__convbond.structure)
        if self.__convbond.structure:
            #print(self.__convbond.structure)
            schedule = qlu.qlSchedule_from_Structure(self.__convbond.structure)
            convertible = ql.ConvertibleFixedCouponBond(exercise,
                                                    self.__convbond.conversion_ratio,
                                                    dividend_schedule,
                                                    callability_schedule, 
                                                    credit_spread_handle,
                                                    qlu.datestr_to_qldate(self.__convbond.issue_date),
                                                    0,
                                                    [self.__convbond.coupon/100],
                                                    qlc.ql_day_count[self.__convbond.settings.day_count],
                                                    schedule,
                                                    self.__convbond.redemption)
            return convertible
        else:
            return None


    def __exercise(self, value_date: str, ):
        
        if self.__convbond.exercise_type == qle.OptionExercise.american:
            vdate = qlu.datestr_to_qldate(value_date)
            mdate = qlu.datestr_to_qldate(self.__convbond.maturity)
            return ql.AmericanExercise(vdate, mdate)
        else:
            edate = qlu.datestr_to_qldate(self.__convbond.european_expiry)
            return ql.EuropeanExercise(edate)




    def __call_schedule_from_option_schedules(self):
        callschedule = self.__convbond.call_list
        putschedule = self.__convbond.put_list
        schedule = callschedule + putschedule
        sorted_schedule = sorted(schedule, key=lambda d: d.date)
        #print(sorted_schedule)
        option_schedule = ql.CallabilitySchedule()
        for sche in sorted_schedule:
            option_price  = ql.CallabilityPrice(sche.price, 
                                                sche.price_type)
            optionality = ql.Callability(option_price, 
                                        sche.option_type,
                                        qlu.datestr_to_qldate(sche.date))
            option_schedule.append(optionality)
        return option_schedule
    

    def __dividend_schedule_from_dividend_structure(self):
        dividend_schedule = ql.DividendSchedule() # No dividends
        for cf in self.__convbond.dividend_structure:
            ql_fixeddividend = ql.FixedDividend(cf.amount, 
                                            qlu.datestr_to_qldate(cf.date))
            dividend_schedule.append(ql_fixeddividend)
        return dividend_schedule


    def create_dividend_structure_from_dividend_yield(self, 
                                                    value_date: str,
                                                    qlcalendar):
        self.__convbond.dividend_structure = []
        dividend_amount = 0.01 * self.__convbond.dividend_yield * \
                        self.__convbond.stock_price
        next_dividend_date = qlu.datestr_to_qldate(value_date)
        mdate = qlu.datestr_to_qldate(self.__convbond.maturity)

        while next_dividend_date < mdate:
            next_dividend_date = qlcalendar.advance(next_dividend_date, 1, ql.Years)
            cf = {"date": next_dividend_date.ISO(), "amount": dividend_amount}
            cf_class = pymodels.CashFlow(**cf)
            self.__convbond.dividend_structure.append(cf_class)
        #print(self.__convbond.dividend_structure)


    def create_coupon_structure_from_qlschedule(self):
        #downcast self__convbond to FixedRateBond class
        thedict = self.__convbond.dict(exclude={'redemption',
                                            'conversion_price',
                                            'conversion_ratio',
                                            'dividend_yield',
                                            'dividend_structure',
                                            'stock_price',
                                            'call_info',
                                            'put_info',
                                            'exercise_type',
                                            'european_expiry',
                                            'credit_spread'})
        thebond = pymodels.FixedRateBond(**thedict)
        qlSchedule = qlu.qlSchedule2(thebond, self.__qlcalendar)
        self.__convbond.structure = qlu.structure_from_qlSchedule(thebond, qlSchedule)
        