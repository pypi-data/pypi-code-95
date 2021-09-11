import yfinance as yf
from datetime import datetime
import math
import warnings

class Ticker:
    """
    Technical Stock Analysis Toolkit

    Attributes
    ----------
    ticker: str
        Stock that is being analyzed
    interval: str
        Time interval used to calculate indicators
    period: str
        Period of time to use while retriving historical data

    Methods
    -------
    get_dataframe()
        Returns dataframe containing historic ticker information
    get_price()
        Returns current stock price
    get_exponential_moving_average(periods=9)
        Returns Exponential Moving Average
    get_simple_moving_average(periods=9)
        Returns Simple Moving Average
    get_relative_strength_index(periods=14)
        Returns Relative Strength Index
    get_moving_average_convergence_divergence(slow_period=26, fast_period=12)
        Returns Moving Average Convergence Divergence
    get_volume_weighted_average_price()
        Returns Volume Weighted Average Price
    get_stochtastic(slow_period=14, fast_period=3)
        Returns Stochtastic
    get_bollinger_bands(standard_deviations=2, periods=20)
        Returns Bollinger Bands
    get_volume_oscillator(slow_period=10, fast_period=5)
        Returns Volume Oscillator
    get_percentage_price_oscillator(slow_period=26, fast_period=12)
        Returns Percentage Price Oscillator
    get_commodity_channel_index(periods=20)
        Returns Commodity Channel Index
    """

    def __init__(self, ticker, interval="1d", period="3mo"):
        """
        Parameters
        ----------
        ticker: str
            Stock that is being analyzed
        interval: str
            Chart interval, i.e. 5m
        period: str
            How far back do you want to retrive, i.e. 3mo

        Returns
        -------
        None
        """
        warnings.filterwarnings("ignore")
        self.ticker = ticker.upper()
        self.interval = interval
        self.period = period

    def get_dataframe(self):
        """
        Returns
        -------
        dataframe
            A dataframe containing hisorical ticker information
        """
        df = yf.download(self.ticker, interval=self.interval, period=self.period, progress=False, threads=False)

        return df

    def get_price(self):
        """
        Returns
        -------
        float
            Price
        """
        df = self.get_dataframe()

        return df["Close"].iloc[-1]

    def get_exponential_moving_average(self, periods=9):
        """
        Paramaters
        ----------
        periods: int 
            Number of candles used to calculate Exponential Moving Average

        Returns
        -------
        float
            Exponential Moving Average
        """
        df = self.get_dataframe()

        df["ema"] = df["Close"].ewm(span=periods, adjust=False).mean()

        return df["ema"].iloc[-1]

    def get_simple_moving_average(self, periods=9):
        """
        Parameters
        ----------
        periods: int 
            Number of candles used to calcuate Simple Moving Average

        Returns
        -------
        float
            Simple Moving Average
        """
        df = self.get_dataframe()

        df["sma"] = df["Close"].rolling(window=periods).mean()

        return df["sma"].iloc[-1]

    def get_relative_strength_index(self, periods=14):
        """
        Parameters
        ----------
        periods: int 
            Number of candles used to calculate Relative Strength Index

        Returns
        -------
        float
            Relative Strength Index
        """
        df = self.get_dataframe()

        df["Delta"] = df["Close"].diff()
        df["Gain"] = df["Delta"].clip(lower=0)
        df["Loss"] = abs(df["Delta"].clip(upper=0))

        df["AverageGain"] = df["Gain"].ewm(com=periods - 1, adjust=False).mean()
        df["AverageLoss"] = df["Loss"].ewm(com=periods - 1, adjust=False).mean()

        df["RS"] = df["AverageGain"] / df["AverageLoss"]
        df["RSI"] = 100 - (100 / (1 + df["RS"]))

        return df["RSI"].iloc[-1]

    def get_moving_average_convergence_divergence(self, slow_period=26, fast_period=12):
        """
        Parameters
        ----------
        slow_period: int 
            Number of candles used to calcualte slow Exponential Moving average
        fast_period: int 
            Number of candles used to calcuate fast Exponential Moving average

        Returns
        -------
        dict
            A dictionary containing both the Moving Average Convergence Divergence line and signal line
        """
        df = self.get_dataframe()

        df["Fast"] = df["Close"].ewm(span=slow_period, adjust=False).mean()
        df["Slow"] = df["Close"].ewm(span=fast_period, adjust=False).mean()
        df["MACD"] = df["Fast"] - df["Slow"]
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        return {"macd": df["MACD"].iloc[-1], "signal": df["Signal"].iloc[-1]}

    def get_volume_weighted_average_price(self):
        """
        Returns
        -------
        float
            Volume Weighted Average Price
        """
        df = self.get_dataframe()
        try:
            df = df.loc[datetime.now().replace(hour=9, minute=29, second=0):]

            df["Typical"] = (df["High"] + df["Low"] + df["Close"]) / 3
            df["VP"] = df["Typical"] * df["Volume"]
            df["CVP"] = df["VP"].sum()
            df["CV"] = df["Volume"].sum()
            df["VWAP"] = df["CVP"] / df["CV"]

            if df["VWAP"].iloc[-1] == None:
                df["VWAP"].iloc[-1] = df["Close"].iloc[-1]

            return df["VWAP"].iloc[-1]
        except:
            raise Exception("Error, VWAP is an intrday indicator, reduce interval")

    def get_stochtastic(self, slow_period=14, fast_period=3):
        """
        Parameters
        ----------
        slow_period: int 
            Number of candles used to calcualte K value
        fast_period: 
            Number of candles used to calulate D value

        Returns
        -------
        dict
            A dictionary containing both stochtastic values, K and D
        """
        df = self.get_dataframe()

        df["PeriodLow"] = df["Low"].rolling(slow_period).min()
        df["PeriodHigh"] = df["High"].rolling(slow_period).max()
        df["K"] = (df["Close"] - df["PeriodLow"]) * 100 / (df["PeriodHigh"] - df["PeriodLow"])
        df["D"] = df["K"].rolling(fast_period).mean()

        return {"K": df["K"].iloc[-1], "D": df["D"].iloc[-1]}

    def get_bollinger_bands(self, standard_deviations=2, periods=20):
        """
        Parameters
        ----------
        standard_deviations: int 
            Number of standrd deviations used to calcualte upper and lower Bollinger Bands
        periods: int 
            Number of candles used to calculate the Bollinger Bands

        Returns
        -------
        dict
            A dictoinary containing all three Bollinger Bands: the upper band, the mean, and the lower band
        """
        df = self.get_dataframe()

        df["Typical"] = (df["High"] + df["Low"] + df["Close"]) / 3
        df["BolMean"] = df["Typical"].rolling(window=periods).mean()

        df["SecTypical"] = (df["Typical"] - df["BolMean"]) ** 2
        df["SecMean"] = df["SecTypical"].rolling(window=periods).mean()

        standard_deviation = math.sqrt(df["SecMean"].iloc[-1])

        df["BolUp"] = df["BolMean"] + standard_deviations * standard_deviation
        df["BolDown"] = df["BolMean"] - standard_deviations * standard_deviation

        return {"bolDown": df["BolDown"].iloc[-1], "bolMean": df["BolMean"].iloc[-1], "bolUp": df["BolUp"].iloc[-1]}

    def get_volume_oscillator(self, slow_period=10, fast_period=5):
        """
        Parameters
        ----------
        slow_period: int 
            Number of candles used to calculate slow Volume Average
        fast_period: int 
            Number of candles used to calculate fast Volume Average

        Returns
        -------
        float
            Volume Osciallator
        """
        df = self.get_dataframe()

        df["Fast"] = df["Volume"].ewm(span=fast_period, adjust=False).mean()
        df["Slow"] = df["Volume"].ewm(span=slow_period, adjust=False).mean()

        df["VOSC"] = ((df["Fast"] - df["Slow"]) / df["Slow"]) * 100

        return df["VOSC"].iloc[-1]

    def get_percentage_price_oscillator(self, slow_period=26, fast_period=12):
        """
        Parameters
        ----------
        slow_period: int 
            Number of candles used to calcualte slow Exponential Moving average
        fastPeriod: int 
            Number of candles used to calcuate fast Exponential Moving average

        Returns
        -------
        float
            Percentage Price Oscillator
        """
        df = self.get_dataframe()

        df["Fast"] = df["Close"].ewm(span=fast_period, adjust=False).mean()
        df["Slow"] = df["Close"].ewm(span=slow_period, adjust=False).mean()

        df["PPO"] = ((df["Fast"] - df["Slow"]) / df["Slow"]) * 100

        return df["PPO"].iloc[-1]

    def get_commodity_channel_index(self, periods=20):
        """
        Parameters
        ----------
        periods: int
            Number of candles used to calcualte Commodity Channel Index

        Returns
        -------
        float
            Commodity Channel Index
        """
        df = self.get_dataframe()

        df["Typical"] = (df["High"] + df["Low"] + df["Close"]) / 3
        typical_mean = df["Typical"].rolling(window=periods).mean().iloc[-1]

        df["TypicalDiff"] = abs(df["Typical"] - typical_mean)
        df["MeanDeviation"] = df["TypicalDiff"].rolling(window=periods).mean()

        df["CCI"] = (df["Typical"] - typical_mean) / (0.15 * df["MeanDeviation"]) * 10

        return df["CCI"].iloc[-1]
