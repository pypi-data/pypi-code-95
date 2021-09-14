class Cipher:

    letter_number_list = [[' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1',
                           '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C',
                           'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                           'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
                           'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                           'z', '{', '|', '}', '~'],
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                           26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
                           49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
                           72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94,
                           95]]

    def __init__(self, sentence):
        self.sentence = sentence

    def __repr__(self):
        return f"Variable that gets ENC/DEC is \"{self.sentence}\""

    # OUT
    ####################################################################################################################
    def out_sentence(self):
        print(self.sentence)

    def out_letter_number_list(self):
        output = ""
        for letter in self.letter_number_list[0]:
            output = output + "\n" + f"{letter} = {self.letter_number_list[1][self.letter_number_list[0].index(letter)]}"
        print(output)
    ####################################################################################################################

    # CREATE
    ####################################################################################################################
    # Creates a Letter Number List
    def create_letter_number_list(self, letter_str_or_list):
        parameter_type = str(type(letter_str_or_list))
        letter_number_list = [[], []]
        counter = 1
        if parameter_type == "<class 'str'>" or parameter_type == "<class 'list'>":
            for letter in letter_str_or_list:
                letter_number_list[0].append(letter)
                letter_number_list[1].append(counter)
                counter += 1
        else:
            raise TypeError("parameter is not str or list")
        Cipher.check_letter_number_list(letter_number_list)
        self.letter_number_list = letter_number_list
        return self.letter_number_list
    ####################################################################################################################

    # ENC DEC
    ####################################################################################################################
    # Uses Columns to recombine Letters
    def enc_columns(self, column_number):
        Cipher.integer_check(column_number)
        column_list = []
        if column_number <= 0:
            raise ValueError("column cant be 0 or less")
        else:
            pass
        count = 0
        while count != column_number:
            column_list.append([])
            count += 1
        count= 0
        for letter in self.sentence:
            if count != column_number:
                column_list[count].append(letter)
                count += 1
            else:
                count = 0
                column_list[count].append(letter)
                count += 1
        count = 0
        new_sentence = ""
        while count != column_number:
            for letter in column_list[count]:
                new_sentence = new_sentence + letter
            count += 1
        self.sentence = new_sentence
        return self.sentence

    def dec_columns(self, column_number):
        Cipher.integer_check(column_number)
        sentence_len = len(self.sentence)
        column_len = int(sentence_len / column_number)
        column_len_rest = int(sentence_len % column_number)
        number_list = []
        column_list = []
        count = 0
        while count != column_number:
            column_list.append([])
            number_list.append([])
            count += 1
        count = 0
        while count != column_number:
            number_list[count].append(column_len)
            if count < column_len_rest:
                number_list[count][0] = number_list[count][0] + 1
                count += 1
            else:
                count += 1
        counter_plus = 0
        counter = 0
        for number in number_list:
            count = 0
            while count != number[0]:
                column_list[counter_plus].append(self.sentence[counter])
                counter += 1
                count += 1
            counter_plus += 1
        new_sentence = ""
        current_index = 0
        while current_index != number_list[0][0]:
            for list in column_list:
                try:
                    new_sentence = new_sentence + list[current_index]
                except:
                    pass
            current_index += 1
        self.sentence = new_sentence
        return self.sentence

    # Swaps Letter with Number and Number with Letter
    def enc_letter_to_number(self):
        Cipher.check_letter_number_list(Cipher.letter_number_list)
        Cipher.string_check(self.sentence)
        new_sentence = ""
        len_last_number = len(str(Cipher.letter_number_list[1][-1]))
        for letter in self.sentence:
            number = str(Cipher.letter_number_list[1][Cipher.letter_number_list[0].index(letter)])
            number_len = len(number)
            zero_add = len_last_number - number_len
            new_sentence = new_sentence + ((zero_add * "0") + number)
        self.sentence = new_sentence
        return self.sentence

    def dec_letter_to_number(self):
        Cipher.check_letter_number_list(Cipher.letter_number_list)
        Cipher.string_check(self.sentence)
        new_sentence = ""
        number_list = []
        len_last_number = len(str(Cipher.letter_number_list[1][- 1]))
        counter = 1
        letter_single = ""
        for number in self.sentence:
            if counter <= len_last_number:
                letter_single = letter_single + number
                counter += 1
            else:
                number_list.append(int(letter_single))
                letter_single = number
                counter = 2
        number_list.append(int(letter_single))
        for number in number_list:
            new_sentence = new_sentence + Cipher.letter_number_list[0][Cipher.letter_number_list[1].index(int(number))]
        self.sentence = new_sentence
        return self.sentence

    # Caesar_Cipher shifts the letter with the shift_number
    def enc_caesar_cipher(self, shift_number):
        Cipher.integer_check(shift_number)
        Cipher.check_letter_number_list(Cipher.letter_number_list)
        Cipher.string_check(self.sentence)
        new_sentence = ""
        len_list = len(Cipher.letter_number_list[0])
        for letter in self.sentence:
            if Cipher.letter_number_list[0].index(letter) + shift_number > len_list:
                high_len = Cipher.letter_number_list[0].index(letter) + shift_number
                multiplier = int(high_len / len_list)
                end_len = high_len - (multiplier * len_list)
                new_sentence = new_sentence + Cipher.letter_number_list[0][end_len]
            else:
                high_len = Cipher.letter_number_list[0].index(letter) + shift_number
                new_sentence = new_sentence + Cipher.letter_number_list[0][high_len]
        self.sentence = new_sentence
        return self.sentence

    def dec_caesar_cipher(self, shift_number):
        Cipher.integer_check(shift_number)
        Cipher.check_letter_number_list(Cipher.letter_number_list)
        Cipher.string_check(self.sentence)
        new_sentence = ""
        len_list = len(Cipher.letter_number_list[0])
        for letter in self.sentence:
            if Cipher.letter_number_list[0].index(letter) - shift_number < 0:
                low_len = shift_number - Cipher.letter_number_list[0].index(letter)
                multiplier = int(low_len / len_list)
                end_len = - (low_len - (multiplier * len_list))
                new_sentence = new_sentence + Cipher.letter_number_list[0][end_len]
            else:
                low_len = Cipher.letter_number_list[0].index(letter) - shift_number
                new_sentence = new_sentence + Cipher.letter_number_list[0][low_len]
        self.sentence = new_sentence
        return self.sentence
    ####################################################################################################################

    # CHECK
    ####################################################################################################################
    # Check letter number list
    @classmethod
    def check_letter_number_list(cls, list):
        if len(list[0]) == len(list[1]):
            pass
        else:
            raise IndexError("more letters or numbers. letters and numbers should have the same number of indexes")
        counter = 1
        for letter in list[0]:
            if str(type(letter)) == "<class 'str'>":
                pass
            else:
                raise TypeError("letters should be from type str")
            if len(letter) == 1:
                pass
            else:
                raise ValueError("to much letters in one index. should be one letter per index")
            if list[0].count(letter) == 1:
                pass
            else:
                raise ValueError("there should be no letter duplicate")
        for number in list[1]:
            if str(type(number)) == "<class 'int'>":
                pass
            else:
                raise TypeError("numbers should be from type int")
            if number == counter:
                counter += 1
            else:
                raise ValueError("numbers should start at 1 and raise everytime by 1")

    # Check for right input Types
    @classmethod
    def tuple_check(cls, tuple):
        tuple_bool = str(type(tuple)) == "<class 'tuple'>"

        if tuple_bool:
            pass
        else:
            raise TypeError(str(type(tuple)).replace("<class '", "").replace("'>", "") + "is given but tuple should be given")

    @classmethod
    def float_check(cls, float):
        float_bool = str(type(float)) == "<class 'float'>"

        if float_bool:
            pass
        else:
            raise TypeError(str(type(float)).replace("<class '", "").replace("'>", "") + " is given but float should be given")

    @classmethod
    def list_check(cls, list):
        list_bool = str(type(list)) == "<class 'list'>"

        if list_bool:
            pass
        else:
            raise TypeError(str(type(list)).replace("<class '", "").replace("'>", "") + " is given but list should be given")

    @classmethod
    def dictionary_check(cls, dictionary):
        dictionary_bool = str(type(dictionary)) == "<class 'dict'>"

        if dictionary_bool:
            pass
        else:
            raise TypeError(
                str(type(dictionary)).replace("<class '", "").replace("'>", "") + " is given but dictionary should be given")

    @classmethod
    def integer_check(cls, integer):
        integer_bool = str(type(integer)) == "<class 'int'>"

        if integer_bool:
            pass
        else:
            raise TypeError(
                str(type(integer)).replace("<class '", "").replace("'>", "") + " is given but integer should be given")

    @classmethod
    def string_check(cls, string):
        string_bool = str(type(string)) == "<class 'str'>"

        if string_bool:
            pass
        else:
            raise TypeError(
                str(type(string)).replace("<class '", "").replace("'>", "") + " is given but string should be given")
    ####################################################################################################################
