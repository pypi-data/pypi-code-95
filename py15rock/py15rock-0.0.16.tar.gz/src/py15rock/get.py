import requests    
import pandas as pd
import json

class config:
    api_key = None
    api_endpoint = 'https://api.15rock.com'

#actual api calls
async def requestCompanyReturning(ticker, endpoint):
    r = requests.get(f'{config.api_endpoint}/company/{ticker}/{endpoint}', headers={'Authorization': f'{config.api_key}'})
    df = pd.read_json(r.content)
    return df

#api calls for endpoints that require years 
async def requestCompanyReturningYears(ticker, years, endpoint, token):
    r = requests.get(f'{config.api_endpoint}/company/{ticker}/{endpoint}/{years}', headers={'Authorization': f'{config.api_key}'})
    df = pd.read_json(r.content)
    return df

#api call for fund level analytics
async def requestFundAnalytics(fund_ticker, endpoint):
    r = requests.get(f'{config.api_endpoint}/fund/{fund_ticker}/{endpoint}', headers={'Authorization': f'{config.api_key}'})
    df = pd.read_json(r.content)
    return df

#api call for portflio level analytics
async def requestPortflioAnalytics(data, endpoint):
    r = requests.post(f'{config.api_endpoint}/portfolio/analytics/{endpoint}', headers={'Authorization': f'{config.api_key}'}, data=data)
    df = pd.read_json(r.content)
    return df

#api call for country level analytics
async def requestCountryAnalytics(countryName, endpoint):
    r = requests.get(f'{config.api_endpoint}/country/{countryName}/{endpoint}', headers={'Authorization': f'{config.api_key}'})
    df = pd.read_json(r.content)
    return df



#company endpoints

async def companyCarbon(ticker):
    df = requestCompanyReturning(ticker, "carbon-footprint")
    return df

async def companyIndustryAverage(ticker):
    df = requestCompanyReturning(ticker, "industry-average")
    return df

async def companyNetincomeCarbon(ticker):
    df = requestCompanyReturning(ticker, "netincome-carbon")
    return df

async def company15rockScore(ticker):
    df = requestCompanyReturning(ticker, "15rock-globalscore")
    return df

async def companyInfo(ticker):
    df = requestCompanyReturning(ticker, "")
    return df

async def companyCalculator(ticker):
    df = requestCompanyReturning(ticker, "equivalencies_calculator")
    return df

async def companyIndustrySum(ticker):
    df = requestCompanyReturning(ticker, "industry-sum")
    return df

async def companyEmissionsEfficiency(ticker):
    df = requestCompanyReturning(ticker, "EmissionsEfficiency")
    return df

async def companyHistoricalPrices(ticker):
    df = requestCompanyReturning(ticker, "historicalPrices")
    return df

async def companyCOGS(ticker):
    df = requestCompanyReturning(ticker, "cogs")
    return df

async def companySumHistoricCarbon(ticker, years):
    df = requestCompanyReturningYears(ticker, years, "sumhistoriccarbon")
    return df

async def companyTempConversation(ticker, years):
    df = requestCompanyReturningYears(ticker, years, "temperatureconversion")
    return df

async def companyCarbonAlpha(ticker, years):
    df = requestCompanyReturningYears(ticker, years, "carbonAlpha")
    return df

async def companyCarbonTransitionRisk(ticker, years):
    df = requestCompanyReturningYears(ticker, years, "CarbonTransitonRisk")
    return df

async def companyCarbonBudget(ticker):
    df = requestCompanyReturning(ticker, "carbonbudget")
    return df

async def companyCarbonTax(ticker):
    df = requestCompanyReturning(ticker, "carbontax")
    return df

async def companyCarbonGrowthRate(ticker):
    df = requestCompanyReturning(ticker, "carbongrowthrate")
    return df

async def companyCarbonProductionEfficency(ticker):
    df = requestCompanyReturning(ticker, "productionefficency")
    return df

async def companyCarbonCapture(ticker):
    df = requestCompanyReturning(ticker, "carboncapture")
    return df




async def getCompany(ticker, endpoint):
    r = requests.get(f'{config.api_endpoint}/company/{ticker}/{endpoint}', headers={'Authorization': f'{config.api_key}'})
    df = pd.read_json(r.content)
    return df


#fund data
async def getFundHoldings(fund_ticker):
    df = requestFundAnalytics(fund_ticker, "holdings")
    return df


#portfolio analytics
async def getPortfolioCOGS(holdings_list, agg="sum"):
    data = {'tickers' : holdings_list, "func":agg}
    data = json.dumps(data)
    df = requestPortflioAnalytics(data=data, endpoint="cogs")
    return df

async def getPortfolioCarbon(holdings_list, agg="sum"):
    data = {'tickers' : holdings_list, "func":agg}
    data = json.dumps(data)
    print(data)
    df = requestPortflioAnalytics(data=data, endpoint="carbon-footprint")
    return df

async def getPortfolioHistoricalPrices(holdings_list):
    data = {'tickers' : holdings_list}
    data = json.dumps(data)
    print(data)
    df = requestPortflioAnalytics(data=data, endpoint="historicalprices")
    return df


#country data
async def getCountryCarbon(countryName):
    df = requestCountryAnalytics(countryName, "carbon")
    return df


async def getCountryTax(countryName):
    df = requestCountryAnalytics(countryName, "tax")
    return df


#industry