def isAnagram(self,word1,word2):
        """
        check is anagram or not
        .. versionadded:: 0.0.2
        """
        word1=str(word1).lower()
        word2=str(word2).lower()
        return set(word1)==set(word2)
