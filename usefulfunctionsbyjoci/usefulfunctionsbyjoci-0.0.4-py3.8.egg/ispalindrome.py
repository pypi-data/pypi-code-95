def isPalindrome(self,word):
        """
        check is Palindrome or not
        .. versionadded:: 0.0.2
        """
        word = str(word).lower()
        return word==word[::-1]