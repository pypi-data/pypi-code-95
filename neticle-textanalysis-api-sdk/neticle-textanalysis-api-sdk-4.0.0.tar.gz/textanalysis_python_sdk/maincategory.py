from .category import Category

class MainCategory(object):

    def __init__(self, jsonresponse):
        self.__code = jsonresponse['code']
        self.__label = jsonresponse['label']
        self.__number_of_mentions = jsonresponse['numberOfMentions']
        self.__revelance_score = jsonresponse['relevanceScore']
        self.__type = jsonresponse['type']
        self.__categories = []
        categories = jsonresponse["categories"]
        for c in categories:
            self.__categories.append(Category(c))

    def getCode(self):
        '''
        Code of the category.
        :returns: 
        '''
        return self.__code

    def getLabel(self):
        '''
        Label of the category
        :returns: 
        '''
        return self.__label

    def getNumberOfMentions(self):
        '''
        Number of mentions in the category.
        :returns: 
        '''
        return self.__number_of_mentions
    
    def getRevelanceScore(self):
        '''
        Revelance score of the category.
        :returns: 
        '''
        return self.__revelance_score

    def getType(self):
        '''
        Type of the category.
        :returns: 
        '''
        return self.__type
    
    def getCategories(self):
        '''
        All the sub categories of the category.
        :returns: 
        '''
        return self.__categories