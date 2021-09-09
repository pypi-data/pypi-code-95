def nearestIntPalindrome(self,num):
        """
        nearest panagram for integer
        .. versionadded:: 0.0.2
        """
        num=int(num)
        i=0
        while i>=0:
            if str(num+i) == str(num+i)[::-1]:
                return str(num+i)+" is the nearest Palindrome."
                break
            elif str(num-i) == str(num-i)[::-1]:
                return str(num-i)+" is the nearest Palindrome."
                break
            else:
                i+=1