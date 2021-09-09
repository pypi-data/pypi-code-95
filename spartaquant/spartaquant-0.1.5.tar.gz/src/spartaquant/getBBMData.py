try:
    import blpapi
    from optparse import OptionParser
except:
    pass

import pandas as pd
import datetime
import numpy as np


# To do :
# 28.12.2018 : Manage different type of date format 
# 06.01.2019 : getDataMemb entre deux dates

class getBBMData:
    # Warning, it is possible specific fields give different results, like : FUT_CHAIN (see commo carry to understand how we deal with it)

    def __init__(self):
        self.bPrintLog = True
        self.dictRes = dict()
        self.initErrorArr()

    def initErrorArr(self):
        self.errorArr = dict()
        self.errorArr['field'] = []
        self.errorArr['security'] = []
        self.errorArr['fieldErrorMsg'] = []

    def setBPrintLog(self, bPrint):
        self.bPrintLog = bPrint

    def getErrorMessage(self):
        return self.errorArr

    def testIfActiveConnexion(self):
        sessionOptions = blpapi.SessionOptions()
        options = self.parseCmdLine()
        sessionOptions.setServerHost(options.host)
        sessionOptions.setServerPort(options.port)
        # Create a Session
        session = blpapi.Session(sessionOptions)
        bStartSession = session.start()
        if not bStartSession:
            return False
        else:
            return True

    def parseCmdLine(self):
        parser = OptionParser(description="Retrieve reference data.")
        parser.add_option("-a",
                          "--ip",
                          dest="host",
                          help="server name or IP (default: %default)",
                          metavar="ipAddress",
                          default="localhost")
        parser.add_option("-p",
                          dest="port",
                          type="int",
                          help="server port (default: %default)",
                          metavar="tcpPort",
                          default=8194)
        parser.add_option("-f", "--file", dest="filename",
                          help="parseCmdLine", metavar="FILE")
        parser.parse_args()
        (options, args) = parser.parse_args()

        return options

    def getData(self, tickers, fields, startDate=None, endDate=None, optionsOverride=None, prefixType=""):
        # Example of prefixType :
        # "" => For Bloomberg Ticker
        # "isin" => For ISIN
        # Other type works like : "cusip", "sedol", "bsid", "bsym", "buid", "bpkbl", "eid"
        # Example of optionsOverride :
        # If we want to specify optionsOverride, startDate and endDate become mandatory inputs (we can put None,None if we do not care about those inputs)
        # optionsOverride = (('nonTradingDayFillOption','non_trading_weekdays'), Possible fields :  (NON_TRADING_WEEKDAYS | ALL_CALENDAR_DAYS | ACTIVE_DAYS_ONLY)
        #                    ('nonTradingDayFillMethod','PREVIOUS_VALUE'),       Possible fields :  (PREVIOUS_VALUE | NIL_VALUE)
        #                    ('currency','USD'),
        #                   )
        #
        # Example to extract a field at a specific previous date :
        # optionsOverride = (('nonTradingDayFillMethod','PREVIOUS_VALUE'),
        #                    ('nonTradingDayFillOption','NON_TRADING_WEEKDAYS')
        #                   )
        # We put one date (same date for start and end)
        # df_data = getBBMDataObj.getData(ticker, field, date, date, optionsOverride)
        #
        #
        # THIS WORKS FOR REFERENCE DATA RESPONSE
        # optionsOverride = (('SETTLE_DT',parser.parse(date).strftime("%Y%m%d")),
        #                   )
        #
        #
        # optionsOverride = (('nonTradingDayFillMethod','PREVIOUS_VALUE'),
        #      ('periodicityAdjustment','CALENDAR'),
        #       ('periodicitySelection','DAILY')
        #      )

        global options
        options = self.parseCmdLine()
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost(options.host)
        sessionOptions.setServerPort(options.port)

        self.initErrorArr()
        self.dictRes['res'] = 1
        self.dictRes['message'] = ""

        # Create a Session
        session = blpapi.Session(sessionOptions)

        # Start a Session
        if not session.start():
            print("Failed to start session.")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "You are not connected to Bloomberg..."
            return

        if not session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "We are not able to load the Bloomberg api, please check that you have a Bloomberg terminal installed on your machine"
            return

        refDataService = session.getService("//blp/refdata")
        parseService = "ReferenceDataResponse"
        if startDate is None:  # Data reference request
            request = refDataService.createRequest("ReferenceDataRequest")
        else:  # Historical data request
            parseService = "HistoricalDataRequest"
            request = refDataService.createRequest("HistoricalDataRequest")

        if prefixType != "":
            prefixType = "/" + prefixType + "/"

        if type(tickers) == list:
            for thisTicker in tickers:
                request.append("securities", prefixType + thisTicker)
        elif type(tickers) == str:
            request.append("securities", prefixType + tickers)
        else:
            print("Ticker does not have the right type (must be string or list)")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "Ticker does not have the right type (must be string or list)"
            return

        if type(fields) == list:
            for field in fields:
                request.append("fields", field)
        elif type(fields) == str:
            request.append("fields", fields)
        else:
            print("Fields does not have the right type (must be string or list)")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "Fields does not have the right type (must be string or list)"
            return

        if startDate is not None:
            request.set("startDate", startDate)
            if endDate is None:
                now = datetime.datetime.now()
                request.set("endDate", now.strftime("%Y%m%d"))
            else:
                request.set("endDate", endDate)

        if optionsOverride is not None:
            if parseService == "HistoricalDataRequest":  # Historical Data Service
                for optionsTmp in optionsOverride:
                    if self.bPrintLog:
                        print("Option : " + str(optionsTmp[0]) + " => " + str(optionsTmp[1]))
                    request.set(optionsTmp[0], optionsTmp[1])
            else:  # Override for Reference Data Service
                for optionsTmp in optionsOverride:
                    o = request.getElement('overrides').appendElement()
                    if self.bPrintLog:
                        print("Option : " + str(optionsTmp[0]) + " => " + str(optionsTmp[1]))
                    o.setElement('fieldId', optionsTmp[0])
                    o.setElement('value', optionsTmp[1])

        # request.set("periodicitySelection", "MONTHLY");

        # print(request)
        session.sendRequest(request)

        dictRes = {}  # Historical Data Service Results BDH
        dataArrRef = []  # Data Ref Service Results BDP
        tickerFldsArr = []
        try:
            # Process received events
            while (True):
                # We provide timeout to give the chance to Ctrl+C handling:
                ev = session.nextEvent(1)
                for msg in ev:
                    # print(msg)
                    if (msg.hasElement("responseError")):
                        print("error " + str(msg))
                        pass

                    ReferenceDataResponse = msg.asElement()

                    if ReferenceDataResponse.hasElement("securityData"):
                        securityDatas = msg.getElement("securityData")

                        # print(parseService)

                        if parseService == "HistoricalDataRequest":  # Historical Data Service
                            # print("HISTORICAL DATA SERVICE")
                            ticker = securityDatas.getElement('security').getValue().replace(prefixType, '')

                            # CHECK IF INVALID SECURITY
                            if securityDatas.hasElement("securityError"):
                                securityErrors = securityDatas.getElement("securityError")
                                self.dictRes['res'] = -1
                                self.dictRes['message'] = "Invalid security"
                                self.errorArr['security'].append(ticker)
                                # CHECK IF INVALID FIELD
                            if securityDatas.hasElement("fieldExceptions"):
                                fieldExceptions = securityDatas.getElement("fieldExceptions")
                                if fieldExceptions.numValues() > 0:
                                    self.dictRes['res'] = -1
                                    self.dictRes['message'] = "Invalid field"
                                    for thisFieldException in fieldExceptions.values():
                                        fieldId = thisFieldException.getElement('fieldId').getValue()
                                        fieldErrorMsg = thisFieldException.getElement('errorInfo').getElement(
                                            'subcategory').getValue()
                                        self.errorArr['field'].append(fieldId)
                                        self.errorArr['fieldErrorMsg'].append(fieldErrorMsg)

                                    print("ERROR FIELDS :")
                                    print(self.errorArr['field'])
                                    print(self.errorArr['fieldErrorMsg'])

                            fldDatas = securityDatas.getElement('fieldData')
                            nbCol = 1
                            if type(fields) == list:
                                nbCol = len(fields)

                            dataArr = np.zeros((len(list(fldDatas.values())), nbCol))
                            datesArr = []

                            for i, fldData in enumerate(fldDatas.values()):
                                thisDate = fldData.getElement('date').getValue()
                                dataFld = []
                                datesArr.append(str(thisDate))
                                if type(fields) == list:
                                    for field in fields:
                                        if fldData.hasElement(field):
                                            thisFld = fldData.getElement(field).getValue()
                                        else:
                                            thisFld = np.nan
                                        dataFld.append(thisFld)
                                else:
                                    if fldData.hasElement(fields):
                                        thisFld = fldData.getElement(fields).getValue()
                                    else:
                                        thisFld = np.nan
                                    dataFld.append(thisFld)
                                dataArr[i, :] = dataFld

                            if type(fields) == list:
                                df = pd.DataFrame(dataArr, columns=fields)
                            elif type(fields) == str:
                                df = pd.DataFrame(dataArr, columns=[fields])
                            df['Date'] = datesArr
                            try:
                               df.index =  datesArr
                            except:
                                pass
                            df.name = ticker
                            df.columns.name = ticker
                            dictRes[ticker] = df

                        else:  # Reference Data Service
                            # print("REFERENCE DATA SERVICE")
                            for securityData in securityDatas.values():
                                dataFld = []
                                ticker = securityData.getElement('security').getValue().replace(prefixType, '')
                                # CHECK IF INVALID SECURITY
                                if securityData.hasElement("securityError"):
                                    securityErrors = securityData.getElement("securityError")
                                    self.dictRes['res'] = -1
                                    self.dictRes['message'] = "Invalid security"
                                    self.errorArr['security'].append(ticker)
                                # CHECK IF INVALID FIELD
                                if securityData.hasElement("fieldExceptions"):
                                    fieldExceptions = securityData.getElement("fieldExceptions")
                                    if fieldExceptions.numValues() > 0:
                                        self.dictRes['res'] = -1
                                        self.dictRes['message'] = "Invalid field"
                                        for thisFieldException in fieldExceptions.values():
                                            fieldId = thisFieldException.getElement('fieldId').getValue()
                                            fieldErrorMsg = thisFieldException.getElement('errorInfo').getElement('subcategory').getValue()
                                            self.errorArr['field'].append(fieldId)
                                            self.errorArr['fieldErrorMsg'].append(fieldErrorMsg)

                                        print("ERROR FIELDS 1 :")
                                        print(self.errorArr['field'])
                                        print(self.errorArr['fieldErrorMsg'])

                                fldData = securityData.getElement('fieldData')
                                # print(fldData)
                                if type(fields) == list:
                                    for field in fields:
                                        if fldData.hasElement(field):
                                            thisFld = fldData.getElement(field).getValue()
                                            if fldData.getElement(field).numValues() > 1:
                                                thisFld = dict()
                                                nameArr = []
                                                for indElm in range(list(fldData.getElement(field).values())[
                                                                        0].numElements()):  # GET THE NUMBER OF KEYS AND THEIR NAME
                                                    nameArr.append(str(
                                                        list(fldData.getElement(field).values())[0].getElement(
                                                            indElm).name()))
                                                    thisFld[nameArr[indElm]] = []

                                                for fldsDataElmnt in fldData.getElement(
                                                        field).values():  # ITERATE OVER THE NUMBER OF ELEMENT
                                                    for indElm in range(list(fldData.getElement(field).values())[
                                                                            0].numElements()):  # ITERATE OVER THE NUMBER OF KEY (Index Member and Percent Weight for the case of INDX_MWEIGHT_HIST for instance)
                                                        thisFld[nameArr[indElm]].append(fldsDataElmnt.getElement(
                                                            fldsDataElmnt.getElement(indElm).name()).getValue())
                                        else:
                                            thisFld = np.nan
                                        dataFld.append(thisFld)
                                else:
                                    if fldData.hasElement(fields):
                                        thisFld = fldData.getElement(fields).getValue()
                                    else:
                                        thisFld = np.nan
                                    dataFld.append(thisFld)

                                tickerFldsArr.append(ticker)
                                dataArrRef.append(dataFld)

                    # Response completly received, so we could exit
                    if ev.eventType() == blpapi.Event.RESPONSE:
                        if parseService == "HistoricalDataRequest":  # Historical Data Service
                            if type(tickers) == list:
                                return dictRes
                            else:
                                return df
                        else:  # Reference Data Service
                            indexRes = [tickers]
                            if type(tickers) == list:
                                indexRes = tickers

                            if type(fields) == list:
                                df = pd.DataFrame(dataArrRef, index=tickerFldsArr, columns=fields)
                            elif type(fields) == str:
                                df = pd.DataFrame(dataArrRef, index=tickerFldsArr, columns=[fields])

                            if type(tickers) == str:
                                df.name = tickers
                                df.columns.name = tickers

                            ticker_df = pd.DataFrame()
                            if type(tickers) == list:
                                ticker_df['TICKER'] = tickers
                            else:
                                ticker_df['TICKER'] = [tickers]

                            df = pd.merge(ticker_df, df, left_on='TICKER', right_index=True, how='inner')
                            if type(tickers) == list:
                                df.index = tickers
                            else:
                                df.index = [tickers]
                            df = df.drop(['TICKER'], axis=1)

                            return df

        finally:
            # Stop the session
            # print("finish")
            session.stop()

    def mergeDf(self, df_, fld, bFillNA=True, bOuter=True):
        factors = list(df_.keys())
        dfData = pd.DataFrame()  # creates a new dataframe that's empty
        cnt = 0
        factorNotNull = []
        for idx, factor in enumerate(factors):
            try:
                if cnt == 0:
                    dfData = df_[factor][[fld, 'Date']]
                    if dfData is not None:
                        cnt = cnt + 1
                else:
                    if bOuter:
                        dfData = pd.merge(dfData, df_[factor][[fld, 'Date']], left_on='Date', right_on='Date',
                                          how='outer')
                    else:
                        dfData = pd.merge(dfData, df_[factor][[fld, 'Date']], left_on='Date', right_on='Date',
                                          how='inner')
                factorNotNull.append(factor)
            except:
                pass

            # print(len(df_[factor]["PX_LAST"]))

        dfData = dfData.sort_values(by=['Date'], ascending=True)
        dfData.index = dfData['Date']
        dfData = dfData.drop(columns=['Date'], axis=1)
        dfData.columns = factorNotNull
        if bFillNA:
            dfData = dfData.fillna(method='ffill')
        return dfData

    def getDataMemb(self, tickers, fields, startDate=None, optionsOverride=None, prefixType=""):

        self.initErrorArr()
        self.dictRes['res'] = 1
        self.dictRes['message'] = ""

        global options
        options = self.parseCmdLine()
        sessionOptions = blpapi.SessionOptions()
        sessionOptions.setServerHost(options.host)
        sessionOptions.setServerPort(options.port)

        # Create a Session
        session = blpapi.Session(sessionOptions)

        # Start a Session
        if not session.start():
            print("Failed to start session.")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "You are not connected to Bloomberg..."
            return

        if not session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            self.dictRes['res'] = -1
            self.dictRes[
                'message'] = "We are not able to load the Bloomberg api, please check that you have a Bloomberg terminal installed on your machine"
            return

        refDataService = session.getService("//blp/refdata")
        parseService = "ReferenceDataResponse"

        if fields == "INDX_MWEIGHT_HIST":
            request = refDataService.createRequest("ReferenceDataRequest")
        else:
            request = refDataService.createRequest("ReferenceDataRequest")

        if prefixType != "":
            prefixType = "/" + prefixType + "/"

        if type(tickers) == list:
            for thisTicker in tickers:
                request.append("securities", prefixType + thisTicker)
        elif type(tickers) == str:
            request.append("securities", prefixType + tickers)
        else:
            print("Ticker does not have the right type (must be string or list)")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "Ticker does not have the right type (must be string or list)"
            return

        if type(fields) == str:
            request.append("fields", fields)
        else:
            print("Fields does not have the right type (must be string or list)")
            self.dictRes['res'] = -1
            self.dictRes['message'] = "Fields does not have the right type (must be string or list)"
            return

        if fields == "INDX_MWEIGHT_HIST":
            if startDate is not None:
                o = request.getElement('overrides').appendElement()
                o.setElement('fieldId', 'END_DT')
                o.setElement('value', startDate)

        if optionsOverride is not None:
            o = request.getElement('overrides').appendElement()
            for optionsTmp in optionsOverride:
                print("Option : " + str(optionsTmp[0]) + " => " + str(optionsTmp[1]))
                o.setElement('fieldId', optionsTmp[0])
                o.setElement('value', optionsTmp[1])

        session.sendRequest(request)

        dictRes = {}  # Historical Data Service Results BDH

        try:
            # Process received events
            while (True):
                # We provide timeout to give the chance to Ctrl+C handling:
                ev = session.nextEvent(0)
                for msg in ev:
                    if (msg.hasElement("responseError")):
                        print(msg)
                        pass

                    ReferenceDataResponse = msg.asElement()
                    if ReferenceDataResponse.hasElement("securityData"):
                        securityDatas = msg.getElement("securityData")
                        for securityData in securityDatas.values():
                            dataFld = []
                            ticker = securityData.getElement('security').getValue().replace(prefixType, '')

                            # CHECK IF INVALID SECURITY
                            if securityData.hasElement("securityError"):
                                securityErrors = securityData.getElement("securityError")
                                self.dictRes['res'] = -1
                                self.dictRes['message'] = "Invalid security"
                                self.errorArr['security'].append(ticker)
                                
                            # CHECK IF INVALID FIELD
                            if securityData.hasElement("fieldExceptions"):
                                fieldExceptions = securityData.getElement("fieldExceptions")
                                if fieldExceptions.numValues() > 0:
                                    self.dictRes['res'] = -1
                                    self.dictRes['message'] = "Invalid field"
                                    for thisFieldException in fieldExceptions.values():
                                        fieldId = thisFieldException.getElement('fieldId').getValue()
                                        fieldErrorMsg = thisFieldException.getElement('errorInfo').getElement('subcategory').getValue()
                                        self.errorArr['field'].append(fieldId)
                                        self.errorArr['fieldErrorMsg'].append(fieldErrorMsg)

                                    print("ERROR FIELDS 2 :")
                                    print(self.errorArr['field'])
                                    print(self.errorArr['fieldErrorMsg'])


                            if securityData.hasElement("fieldData"):
                                index_mweights = securityData.getElement('fieldData').getElement('INDX_MWEIGHT_HIST').values()
                                idxMembArr = []
                                pctWeightArr = []
                                for index_mweight in index_mweights:
                                    idxMemb = index_mweight.getElement("Index Member").getValue()
                                    pctWeight = index_mweight.getElement("Percent Weight").getValue() / 100
                                    # print(pctWeight)
                                    idxMembArr.append(idxMemb)
                                    pctWeightArr.append(pctWeight)

                                df = pd.DataFrame(idxMembArr, columns=['MEMBERS'])
                                df['WEIGHT'] = pctWeightArr
                                df.columns.name = ticker
                                dictRes[ticker] = df
                            else:
                                df = pd.DataFrame()
                                dictRes[ticker] = df

                # Response completly received, so we could exit
                if ev.eventType() == blpapi.Event.RESPONSE:
                    if type(tickers) == list:
                        return dictRes
                    else:
                        return df
        finally:
            # Stop the session
            session.stop()