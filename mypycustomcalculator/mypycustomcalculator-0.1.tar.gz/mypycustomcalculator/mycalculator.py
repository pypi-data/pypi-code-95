class Calculator:
    def __init__(self,num1,num2):
        self.num1 = num1
        self.num2 = num2

    def add(self):
        r = self.num1 + self.num2
        result = (
            "The sum of " + str(self.num1) + " and " + str(self.num2) + " is " + str(r)
        )
        #print(result)
        return result

    def subtract(self):
        r = self.num1 - self.num2
        result = (
            "The difference of "
            + str(self.num1)
            + " and "
            + str(self.num2)
            + " is "
            + str(r)
        )
        #print(result)
        return result

    def multiply(self):
        r = self.num1 * self.num2
        result = (
            "The product of "
            + str(self.num1)
            + " and "
            + str(self.num2)
            + " is "
            + str(r)
        )
        #print(result)
        return result

    def divide(self):
        r = self.num1 / self.num2
        result = (
            "The quotient when "
            + str(self.num1)
            + " is divided by "
            + str(self.num2)
            + " is "
            + str(r)
        )
        #print(result)
        return result