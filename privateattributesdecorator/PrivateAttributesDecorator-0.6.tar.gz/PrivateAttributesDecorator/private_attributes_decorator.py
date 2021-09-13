# -----------------------------------------------------------
# Module to increase encapsulation in Python, not allowing the access to private members outside their classes
#
# (C) 2021 Antonio Pérez, Spain
# Released under MIT License
# email ingovanpe@gmail.com
# -----------------------------------------------------------

# The module inspect is imported as it will help us to determine whether an attribute is being called from the class
# or outside the class
import inspect


def private_attributes_dec(*args, **kwargs):
    """We pass a series a strings with the name of public attributes we want to turn private and this decorator
    will make them and private attributes in the class not accessible or modifiable
    Also if we pass a keyword parameter called allow_deep_copy set to True, we will allow the use of the function
    deepcopy from the module copy in the instances of this class. If we don't provide it or we set it to False and
    we set a private attribute, we will raise an AttributeError when trying to use that function"""
    def private_members_decorator(class_):
        # This is the part of the decorator who gets the class we are modifying in the attribute class_
        # We create two new members in our class that are basically clones of the magic methods to get and attribute
        # and set an attribute
        class_.__getattr__orig = class_.__getattribute__
        class_.__setattr__orig = class_.__setattr__

        def new_getattr(self, name: str):
            """This method will modify how the magic method to get attributes works, making impossible for developers
            to get a private attribute or a public attribute we set as private in the decorator outside the class"""
            # We get the current frame where the attribute was called from
            f: inspect.FrameInfo = inspect.currentframe()
            # By default, we will consider that it is not being called from the class (or a subclass) or in case we want
            # to allow it (allow_deep_copy) from the module copy and function deepcopy to create a deepcopy of the
            # object. However, we will check if that is the case using the current frame (f) and checking if it also
            # being called from a subclass or from the module copy and function deepcopy and in that case
            # we set it to True
            special_case: bool = False
            # By default, we assume we are not doing a deepcopy of an instance from this class
            deep_copy: bool = False
            # If we set the keyword parameter allow_deep_copy to True in the decorator, we check if we are indeed
            # trying to create a deepcopy of an object of our decorated class
            if "allow_deep_copy" in kwargs.keys() and kwargs["allow_deep_copy"] == True:
                # We get the previous frames
                previous_frames = inspect.getouterframes(f)
                for f1 in previous_frames:
                    # If in our of those frames the file executed is copy.py and the function is deepcopy
                    if f1.filename.endswith("copy.py") and f1.function == "deepcopy":
                        # We are indeed trying to create a deep copy of an object of this class. Therefore, we set
                        # the control parameter deep_copy to True and break the loop as we don´t have to keep searching
                        deep_copy = True
                        break
            # So if the attribute was called inside our class or one of its subclasses or we are trying to perform
            # a deepcopy
            if ('self' in f.f_back.f_locals and issubclass(type(f.f_back.f_locals['self']), class_)) or deep_copy:
                # It is an special case we have to accept
                special_case = True
            # If the attribute being called is private (starts with __ or _className__ or is in the list of attributes
            # provided to the decorator and it is not a special case (called from a class or subclass or during the
            # process of creating a deepcopy, we raise an AttributeException
            if (name.startswith("__") or name.startswith("_{0}__".format(class_.__name__)) or name in args) and \
                    not special_case:
                raise AttributeError("We can't access private attribute {0}".format(name))
            # Otherwise, we just return the result of calling the copy we did of the usual magic method to get an
            # attribute (so we are returning that attribute)
            return class_.__getattr__orig(self, name)

        def new_setattr(self, name: str, value):
            """This method will modify how the magic method to set attributes works, making impossible for developers
            to set a private attribute or a public attribute we set as private in the decorator outside the class
            to a new value"""
            f: inspect.FrameInfo = inspect.currentframe()
            # By default, we will consider that it is not being called from the class (or a subclass) or in case we want
            # to allow it (allow_deep_copy) from the module copy and function deepcopy to create a deepcopy of the
            # object. However, we will check if that is the case using the current frame (f) and checking if it also
            # being called from a subclass or from the module copy and function deepcopy and in that case
            # we set it to True
            special_case: bool = False
            # By default, we assume we are not doing a deepcopy of an instance from this class
            deep_copy: bool = False
            # If we set the keyword parameter allow_deep_copy to True in the decorator, we check if we are indeed
            # trying to create a deepcopy of an object of our decorated class
            if "allow_deep_copy" in kwargs.keys() and kwargs["allow_deep_copy"] == True:
                # We get the previous frames
                previous_frames = inspect.getouterframes(f)
                for f1 in previous_frames:
                    # If in our of those frames the file executed is copy.py and the function is deepcopy
                    if f1.filename.endswith("copy.py") and f1.function == "deepcopy":
                        # We are indeed trying to create a deep copy of an object of this class. Therefore, we set
                        # the control parameter deep_copy to True and break the loop as we don´t have to keep searching
                        deep_copy = True
                        break
            # So if the attribute was called inside our class or one of its subclasses or we are trying to perform
            # a deepcopy
            if ('self' in f.f_back.f_locals and issubclass(type(f.f_back.f_locals['self']), class_)) or deep_copy:
                # It is an special case we have to accept
                special_case = True
            # If the attribute being called is private (starts with __ or _className__ or is in the list of attributes
            # provided to the decorator and it is not a special case (called from a class or subclass or during the
            # process of creating a deepcopy, we raise an AttributeException
            if (name.startswith("__") or name.startswith("_{0}__".format(class_.__name__)) or name in args) and \
                    not special_case:
                raise AttributeError("We can't access private attribute {0}".format(name))
            return class_.__setattr__orig(self, name, value)
        # We replace the standard magic methods to get and set attributes with the new ones we defined above
        class_.__getattribute__ = new_getattr
        class_.__setattr__ = new_setattr
        # We return our modified class
        return class_
    # We return the middle decorator
    return private_members_decorator


if __name__ == "__main__":
    # We are providing some examples here:
    # Case 1: Root class and private attribute (starts with __) -> Attribute __d
    # Case 2: Root class and public attribute, however we set it as private using the decorator (We pass the name of the
    # attribute in the decorator) -> Attribute a
    # Case 3: Root class and private attribute, that was turned into a property with a setter and deleter
    @private_attributes_dec("a")
    class Example:
        def __init__(self):
            self.a: int = 12
            self.b: int = 12
            self.c: int = 12
            self.__d: int = 12
            self.__e: int = 12

        # Case 1.2: We call to a method defined in the class that accesses that private attribute
        def get_d(self):
            return self.__d

        # Case 1.3: We call to a method defined in the class that sets that private attribute to a new value
        def set_d(self, value: int):
            self.__d = value

        # Case 2.2: We call to a method defined in the class that accesses that attribute we made private
        def get_a(self):
            return self.a

        # Case 2.3: We call to a method defined in the class that sets that attribute we made private to a new value
        def set_a(self, value: int):
            self.a = value

        # Case 3.1: Private attribute made property
        @property
        def e(self) -> int:
            return self.__e

        # Case 3.2: Private attribute made a property, setter
        @e.setter
        def e(self, value: int):
            self.__e = value

        # Case 3.3: Private attribute made a property, deleter
        @e.deleter
        def e(self):
            self.__e = None

    e: Example = Example()
    # Case 1.1: Trying to access the private attribute outside the class -> We will raise an AttributeError
    try:
        print(e._Example__d)
    except AttributeError:
        assert True
        print("The attribute __d (_Example__d) can't be accessed outside the class")
    else:
        assert False
    # Case 1.2: We call to a method defined in the class that accesses that private attribute -> The method works
    try:
        print(e.get_d())
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert True
    # Case 1.3: We call to a method defined in the class that accesses that private attribute -> The method works
    try:
        e.set_d(13)
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert e.get_d() == 13
    # Case 1.4: We try to access __dict__ -> We raise an AttributeError cause __dict__ is now a private attribute
    try:
        print(e.__dict__)
    except AttributeError:
        assert True
        print("The attribute __dict__ can't be accessed outside the class, it's private now")
    else:
        assert False
    # Case 1.5: We try to modify __dict__ -> We raise an AttributeError cause __dict__ is now a private attribute
    try:
        e.__dict__["b"] = 3
    except AttributeError:
        assert True
        print("The attribute __dict__ can't be accessed outside the class, it's private now")
    else:
        assert False
    # Case 2.1: We try to access a public attribute that we altered to make private using the arguments in the decorator
    # -> We raise an AttributeError
    try:
        print(e.a)
    except AttributeError:
        assert True
        print("The attribute a can't be accessed outside the class")
    else:
        assert False
    # Case 2.2: We call to a method defined in the class that accesses that attribute we made private
    # -> The method works
    try:
        print(e.get_a())
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert True
    # Case 2.3: We call to a method defined in the class that accesses that attribute we made private
    # -> The method works
    try:
        e.set_a(13)
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert e.get_a() == 13
    # Case 3.1: We try to access a private attribute that was turned into a property -> We can access the property
    try:
        print(e.e)
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert True
    # Case 3.2: We try to set a new value to a private attribute that where we defined a set method-> The method works
    try:
        e.e = 3
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert e.e == 3
    # Case 3.3: We try to delete a private attribute turned into a property where we set up a deleter -> It works
    try:
        del e.e
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert e.e == None

    # Case 4: Public attribute turned private using the decorator and now handled in the subclass
    # Case 5: Private attribute turned property with setter and deleter
    class SubclassExample(Example):
        def __init__(self):
            Example.__init__(self)

        # Case 4.1: We access public attribute turned private inside a subclass
        def get_a_v2(self):
            return self.a

        # Case 4.2: We set a public attribute turned private inside a subclass
        def set_a_v2(self, value: int):
            self.a = value


    se = SubclassExample()
    # Case 4.1: We access public attribute turned private inside a subclass -> The method works (subclasses can access
    # them)
    try:
        print(se.get_a_v2())
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert True
    # Case 4.2: We call to a method defined in the class that accesses that attribute we made private
    # -> The method works (subclasses can access them)
    try:
        se.set_a_v2(14)
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert se.get_a() == 14
    # Case 5.1: Private attribute turned property with setter and deleter, we try to get the property -> Method works
    try:
        print(se.e)
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert True
    # Case 5.2: Private attribute turned property with setter and deleter, we try to use the setter
    # -> Method works
    try:
        se.e = 5
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert se.e == 5
    # Case 5.3: Private attribute turned property with setter and deleter, we try to use the deleter -> Method works
    try:
        del se.e
    except AttributeError:
        print("Error, we raised an AttributeError")
        assert False
    else:
        assert se.e == None

    # Case 6: We try to do a deepcopy of an object, but we set some parameters as private in its class and did not
    # set the attribute allow_deep_copy to True
    @private_attributes_dec("arg1")
    class NewExample:
        def __init__(self,arg1: int, arg2: int, arg3: int):
            self.arg1: int = arg1
            self__arg2: int = arg2
            self.arg3: int = arg3
    import copy

    ne: NewExample = NewExample(1,2,3)
    # Case 6.1: We try to do a deepcopy of an object, but we set some parameters as private in its class and did not
    # set the attribute allow_deep_copy to True -> deepcopy raises a copy.Error Exception
    try:
        nec = copy.deepcopy(ne)
    except copy.Error:
        print("We did not allow for deep copies so the method raised a copy.Error Exception")
        assert True
    else:
        print("We did not allow for deep copies, but the deep copy was produced. Something is not right here")
        assert False
    # Case 6.2: We set some parameters as private in its class and did not set the attribute allow_deep_copy to True,
    # we try to access one of those new private attributes -> We raise an AttributeError as expected
    try:
        print(ne.arg1)
    except AttributeError:
        print("As before, we can´t access the argument we set as private arg1")
        assert True
    else:
        print("Something is not right here, we should not be able to access private attribute arg1")
        assert False
    # Case 6.3: We set some parameters as private in its class and did not set the attribute allow_deep_copy to True,
    # we try to access one of its public attributes -> We can get the value of the attribute
    try:
        print(ne.arg3)
    except AttributeError:
        print("Something is not working fine, we should be able to access arg3")
        assert False
    else:
        print("We can still access arg3 without issues")
        assert True
    # Case 7: We allowed deep copies in our class and we try to do a deepcopy of an object, we set the some parameters
    # as private in its class
    @private_attributes_dec("arg1",allow_deep_copy=True)
    class NewExampleAllowDeepCopy:
        def __init__(self,arg1: int, arg2: int, arg3: int):
            self.arg1: int = arg1
            self__arg2: int = arg2
            self.arg3: int = arg3


    ned: NewExampleAllowDeepCopy = NewExampleAllowDeepCopy(1, 2, 3)
    # Case 7.1: We allowed deep copies in our class and we try to do a deepcopy of an object, we set the some parameters
    # as private in its class. We try to create a deepcopy of the object -> The copy is created
    try:
        nedc = copy.deepcopy(ned)
    except copy.Error:
        print("We allowed for deep copies but the method raised a copy.Error Exception, something is wrong")
        assert False
    else:
        print("The copy was created without issues")
        print(nedc)
        assert True
    # Case 7.2: We allowed deep copies in our class and we try to do a deepcopy of an object, we set the some parameters
    # as private in its class. We try to get a private attribute -> We raise an AttributeError as expected
    try:
        print(ned.arg1)
    except AttributeError:
        print("As before, we can´t access the argument we set as private arg1")
        assert True
    else:
        print("Something is not right here, we should not be able to access private attribute arg1")
        assert False
    # Case 7.2: We allowed deep copies in our class and we try to do a deepcopy of an object, we set the some parameters
    # as private in its class, we try to access one of its public attributes -> We can get the value of the attribute
    try:
        print(ned.arg3)
    except AttributeError:
        print("Something is not working fine, we should be able to access arg3")
        assert False
    else:
        print("We can still access arg3 without issues")
        assert True