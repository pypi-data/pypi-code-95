VOWELS = ['a','e','i','o','u']


def check_valid(str):
    if str == "":
        return False
    else:
        return True


def count_vowels(str):
    str1 = str.lower()
    counter = {}

    if check_valid(str1):
        for i in range(len(str1)):
            for j in range(len(VOWELS)):
                if str1[i]==VOWELS[j]:
                    if VOWELS[j] not in counter:
                        counter[VOWELS[j]] = 0
                    counter[VOWELS[j]] +=1
        return counter
    else:
        return "String not Valid"