#! /usr/bin/python3

from datetime import date, datetime, timedelta
import sys
import pandas as pd

# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

class Holidays:
    @classmethod
    def to_datetime(self, datestr:str) -> datetime:
        """
        Convert date strings like "20210506" to datetime type.

        Parameters
        ----------
        datestr : str (in '%Y%m%d' format), or valid datetime object.

        Raises
        ------
        ValueError
            * If datestr argument is invalid

        Examples
        --------
        >>> yyyymmdd = "20210530"
        >>> dt = Holidays.to_datetime(yyyymmdd)
        """
        if type(datestr) == type(datetime.now()):
            return datestr

        try:
            return datetime(
                    year=int(datestr[0:4]),
                    month=int(datestr[4:6]),
                    day=int(datestr[6:8]),
                )
        except:
            raise ValueError ("Wrong datestr argument, should be like: '20210526'.")

    @classmethod
    def tradingday(self, tm: datetime) -> bool:
        """
        Return True if given date is a tradingday, or False otherwise

        Parameters
        ----------
        tm : datetime object, or valid date string like "20210530".

        Raises
        ------
        ValueError
            * If tm argument is invalid
        
        Examples
        --------
        >>> dt = datetime.now()
        >>> is_tradingday = tradingday(dt)
        """
        if type(tm) != type(datetime.now()):
            tm = self.to_datetime(tm)

        if int(tm.strftime("%w")) in [6,0]:
            return False

        tm_str = tm.strftime('%m/%d/%Y')

        if tm_str in self.SSEHolidays:
            return False

        return True

    @classmethod
    def prev_tradingday(self, tm:datetime) -> datetime:
        """
        Return the previous tradingday of a given date

        Parameters
        ----------
        tm : datetime object, or valid date string like "20210530".

        Raises
        ------
        ValueError
            * If tm argument is invalid

        Examples
        --------
        >>> dt = datetime.now()
        >>> prev_td = prev_tradingday(dt)
        """
        if type(tm) != type(datetime.now()):
            tm = self.to_datetime(tm)
        ret = tm + timedelta(days=-1)
        while not (self.tradingday(ret)):
            ret = ret + timedelta(days=-1)
        return ret

    @classmethod
    def next_tradingday(self, tm: datetime) -> datetime:
        """
        Return the next tradingday of a given date.

        Parameters
        ----------
        tm : datetime object, or valid date string like "20210530".

        Raises
        ------
        ValueError
            * If tm argument is invalid
            
        Examples
        --------
        >>> dt = datetime.now()
        >>> next_td = next_tradingday(dt)
        """
        if type(tm) != type(datetime.now()):
            tm = self.to_datetime(tm)
        ret = tm + timedelta(days=1)
        while not (self.tradingday(ret)):
            ret = ret + timedelta(days=1)
        return ret

    @classmethod
    def get_holidays(self) -> pd.DataFrame:
        """
        Return a pandas.DataFrame object with only one column
        named 'Dates' containing all the holidays.
            
        Examples
        --------
        >>> h_days = get_holidays()
        """
        ret = pd.DataFrame()
        ret['Dates'] = [datetime.strptime(dt, "%m/%d/%Y") for dt in self.SSEHolidays]
        return ret

    SSEHolidays = [
               '01/01/2018', '02/15/2018', '02/16/2018', '02/17/2018', '02/18/2018', '02/19/2018' ,'02/20/2018',
               '02/21/2018', '04/05/2018', '04/06/2018', '04/07/2018', '04/29/2018', '04/30/2018', '05/01/2018',
               '06/16/2018', '06/17/2018', '06/18/2018', '10/01/2018', '10/02/2018', '10/03/2018',
               '10/04/2018', '10/05/2018', '10/06/2018', '10/07/2018', '02/04/2019', '02/05/2019', '02/06/2019',
               '02/07/2019', '02/08/2019', '02/09/2019', '02/10/2019', '04/05/2019', '04/06/2019', '04/07/2019',
               '05/01/2019', '05/02/2019', '05/03/2019', '05/04/2019', '06/07/2019', '06/08/2019', '06/09/2019',
               '09/13/2019', '09/14/2019', '09/15/2019', '10/01/2019', '10/02/2019', '10/03/2019',
               '10/04/2019', '10/05/2019', '10/06/2019', '10/07/2019', '01/01/2020', '01/24/2020',
               '01/25/2020', '01/26/2020', '01/27/2020', '01/28/2020', '01/29/2020', '01/30/2020',
               '01/31/2020', '02/01/2020', '02/02/2020', '04/04/2020', '04/05/2020', '04/06/2020', '05/01/2020',
               '05/02/2020', '05/03/2020', '05/04/2020', '05/05/2020', '06/25/2020', '06/26/2020', '06/27/2020',
               '10/01/2020', '10/02/2020', '10/03/2020', '10/04/2020', '10/05/2020', '10/06/2020',
               '10/07/2020', '10/08/2020', '01/01/2021', '01/02/2021', '01/03/2021', '02/11/2021', '02/12/2021',
               '02/13/2021', '02/14/2021', '02/15/2021', '02/16/2021', '02/17/2021', '04/03/2021', '04/04/2021',
               '04/05/2021', '05/01/2021', '05/02/2021', '05/03/2021', '05/04/2021', '05/05/2021',
               '06/12/2021', '06/13/2021', '06/14/2021',
               '09/19/2021', '09/20/2021', '09/21/2021', '10/01/2021', '10/02/2021', '10/03/2021', '10/04/2021',
               '10/05/2021', '10/06/2021', '10/07/2021' ]



    
if '__main__' == __name__:
    dt1 = datetime(2021,5,6)
    tm1 = "20210506"
    print(type(dt1), Holidays.to_datetime(dt1), Holidays.tradingday(dt1), Holidays.prev_tradingday(dt1), Holidays.next_tradingday(dt1))
    print(type(tm1), Holidays.to_datetime(tm1), Holidays.tradingday(tm1), Holidays.prev_tradingday(tm1), Holidays.next_tradingday(tm1))
    dt2 = datetime(2021,9,30)
    tm2 = "20210930"
    print(type(dt2), Holidays.to_datetime(dt2), Holidays.tradingday(dt2), Holidays.prev_tradingday(dt2), Holidays.next_tradingday(dt2))
    print(type(tm2), Holidays.to_datetime(tm2), Holidays.tradingday(tm2), Holidays.prev_tradingday(tm2), Holidays.next_tradingday(tm2))

    print(Holidays.get_holidays())