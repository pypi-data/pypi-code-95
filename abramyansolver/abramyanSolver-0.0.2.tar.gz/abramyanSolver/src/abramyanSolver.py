def DigitCount(number):
    counter = 0
    while number != 0:
        counter += 1
        number = number // 10
        
    return counter