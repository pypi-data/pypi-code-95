#coding:gbk

class PoliRobot_Hello:

    def __init__(self,name,age,message):
        self.name = name
        self.age = age
        self.message = message

    def Hello(self):
        print(f"Hello! 我是{self.name} !")

    def Poilage(self):
        print(f"我有 {self.age} 岁了！")

    def Poilmessage(self):
        print(f"{self.message}")