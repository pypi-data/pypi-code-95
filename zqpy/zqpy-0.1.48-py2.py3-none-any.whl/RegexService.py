import re

class RegexServiceClass(object):

    # 获取URL  返回数组
    def GetRegexUrl(self, content):
        urlRegex = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2})*/)+', content)
        return urlRegex 
    
    # 获取"" 中的内容  返回数组
    def GetRegexDoubleQuotation(self, content):
        pattern = re.compile('"(.*)"')
        resultData = pattern.findall(content)
        return resultData 
    
    # 获取a b 之间的内容  返回数组
    def GetRegexBetweenContent(self, a, b, content):
        result = re.findall(".*%s(.*)%s.*"%(a,b),content)
        '''
        print(result)
        for x in result:
            print(x)
        '''
        return result
    
    # 正则获取IP地址
    def GetRegexIP(self, content):
        reip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
        return reip.findall(content)
    
    # 正则截断字符串【按照指定长度】
    def GetCutText(self, text, lenth):
        textArr = re.findall('.{'+str(lenth)+'}', text)
        textArr.append(text[(len(textArr)*lenth):])
        return textArr