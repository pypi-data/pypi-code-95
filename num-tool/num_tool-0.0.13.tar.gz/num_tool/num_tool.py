import random

def random_num_list(a, b, l):
    '''
    returns a list with l random values
    in the range a, b
    '''
    ls = []
    for i in range(l):
        ls.append(random.randint(a, b))
    return ls

def count_duplicates(ls):
    '''
    returns a dictionary with the duplicates of the list ls like this:
    example list ls: ["a", "b", "a"]
    {"a": 2, "b": 1}
    '''
    dc = {}
    for i in set(ls):
        dc[i] = ls.count(i)
    return dc

def remove_duplicates(ls):
    '''
    returns the list ls without duplicates
    '''
    return list(set((ls)))

def is_prime(n):
    '''
    returns True if n is a prime
    and false if n isn´t a prime
    '''
    n = int(n)
    if n < 2:
        return False
    elif n == 2:
        return True
    else:
        for i in range(2, n):
            if (n % i) == 0:
                return False
        return True