"""21.06, nash
__init__ 이 아닌 모듈은 import 시 명시적으로 알려야 한다
"""


def hello():
    print('hello, i am module2')


class MyClass:
    """a test class"""
    # 인스턴스가 생성될 때 실행된다.
    def __init__(self):  # 인수 없음.
        print('init instance')
        self._a = 100  # _: public member
        self.__a = 200  # __: private member

    def foo1(self):
        self.__a += 1
        print('foo1, no args.', self.__a)

    def foo2(self, para):  # 인수 있음
        print('foo2, args: ', para)

