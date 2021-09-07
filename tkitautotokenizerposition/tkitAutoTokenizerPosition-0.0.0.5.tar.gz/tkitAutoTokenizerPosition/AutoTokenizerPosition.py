# -*- coding: utf-8 -*-

class AutoTokenizerPosition:
    """
    用来处理只有关键词的ner数据
    
    起始位置
    tokenizer = BertTokenizer.from_pretrained("clue/albert_chinese_tiny")
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    使用这个可以减少不必要的麻烦
    ## 安装
    ```
    > pip install tkitAutoTokenizerPosition
    
    # or
    
    > pip install git+https://github.com/napoler/tkit-AutoTokenizerPosition
    ```
    
    
    """
    def __init__(self,tokenizer):
        """[summary]
        
        ```
        tokenizer = BertTokenizer.from_pretrained("clue/albert_chinese_tiny")
        tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
        ```
        使用这个可以减少不必要的麻烦
        Args:
            tokenizer ([type]): [description]
        """
        self.tokenizer=tokenizer
        pass
    def pretreatment(self,text):
        """[summary]
        
        预处理文字
        Args:
            text ([type]): [description]
        """
        text=text.lower()
        text=text.replace("\t",tokenizer.pad_token).replace(" ",tokenizer.pad_token)
        text=text.replace("\n",tokenizer.sep_token).replace("\r",tokenizer.sep_token)
        return text
    def getWordList(self,text):
        """[summary]
        
        分词列表
        Args:
            text ([type]): [description]
        """
        text=self.pretreatment(text)
#         text=text.replace(" ",self.tokenizer.pad_token)
        # print(text)
#         word=word.lower()
        return self.tokenizer.tokenize(text)
    def autoLen(self,text):
        """[summary]
        
        获取文本分词后位置
        Args:
            text ([type]): [description]
        """
        realLen=len(self.getWordList(text))
        return realLen
    
    
    def findAll(self,or_text, word):
        """[summary]
        
        获取词语在文字中的所有开始位置
        Args:
            text ([type]): [description]
            word ([type]): [description]
        Yields:
            [type]: [description]
        """
        idx = text.find(word)
        while idx != -1:
            yield idx
            idx = text.find(word, idx + 1)
    def fixPosition(self,text,word,startList=[]):
        """[summary]
        
        自动获取分词后起始位置
        自动匹配所有存在的位置
        
        传入位置可以限制查找的位置
        Args:
            text ([type]): [description]
            word ([type]): [description]
            startList (list, optional): [description]. Defaults to [].
        Yields:
            [type]: [description]
        """

        #获取起始位置
        if len(startList) ==0:
            startList=self.findAll(text, word)
        for start in startList:
            #获取开始
            print(text[:start])
            print(text[:start+len(word)])
            s_start=self.autoLen(text[:start])
        #     print("s_start",s_start)
            end=self.autoLen(text[:start+len(word)])
            # print("s_end", s_start,s_start+startLen)  
            yield s_start,end
    def autoTypeWord(self,text,word,wType=None,startList=[]):
        """[summary]
        Args:
            text ([type]): [description]
            word ([type]): [description]
            wType ([type], optional): [description]. Defaults to None.
            startList (list, optional): [description]. Defaults to [].
        """
        for s_start,s_end in self.fixPosition(text,word,startList=[]):
#             print(s_start,s_end)
#             WordList=self.getWordList(it['text'])
            yield s_start,s_end,wType
