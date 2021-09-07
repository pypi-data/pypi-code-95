# Diet Problem
# Method : Simplex Method
# Using  : run diet_problem() directly

"""
probelm:
    min  c^T x
    s.t. Ax = b
         x >= 0
"""

import sys
import math
import numpy as np
from queue import Queue
from scipy.optimize import linprog

 
class ILP():
    def __init__(self, c, A_ub, b_ub, A_eq=None, b_eq=None):
        self.LOWER_BOUND = -sys.maxsize
        self.UPPER_BOUND = sys.maxsize
        self.opt_val = None                 # optimal solution: object function value
        self.opt_x = None                   # optimal solution: varibles' value
        self.Q = Queue()
        # the constant parameter arrays
        self.c = c
        self.A_eq = A_eq
        self.b_eq = b_eq

        # solve the primary lp problem
        r = linprog(self.c, A_ub, b_ub, A_eq, b_eq)
        if not r.success:
            raise ValueError('Not a feasible problem!')
        # record the data
        self.Q.put((r, A_ub, b_ub))
 
    def solve(self):
        while not self.Q.empty():
            # pop out the base solution
            res, A_ub, b_ub = self.Q.get(block=False)
            # if the solution is worse than the optimal solution, ignore it
            if -res.fun < self.LOWER_BOUND:
                continue
 
            # prevent loop too much with little improve
            res_x = [round(x,4) for x in res.x]
            # print(res_x)
            # if all varibles in x is integer，update the optimal result util now
            if all(list(map(lambda f: f.is_integer(), res_x))):
                if self.LOWER_BOUND < -res.fun:
                    self.LOWER_BOUND = -res.fun 
                if self.opt_val is None or self.opt_val < -res.fun:
                    self.opt_val = -res.fun
                    self.opt_x = res_x 
                continue
            # purne
            else:
                # find the first varible that is not a integer, get its index idx
                idx = 0
                for i, x in enumerate(res_x):
                    if not x.is_integer():
                        break
                    idx += 1
 
                # add new constraint to split into two subproblems with integer constraint
                new_con1 = np.zeros(A_ub.shape[1])
                new_con1[idx] = -1
                new_con2 = np.zeros(A_ub.shape[1])
                new_con2[idx] = 1
                new_A_ub1 = np.insert(A_ub, A_ub.shape[0], new_con1, axis=0)
                new_A_ub2 = np.insert(A_ub, A_ub.shape[0], new_con2, axis=0)
                new_b_ub1 = np.insert(
                    b_ub, b_ub.shape[0], -math.ceil(res_x[idx]), axis=0)
                new_b_ub2 = np.insert(
                    b_ub, b_ub.shape[0], math.floor(res_x[idx]), axis=0)
 
                # solve the subproblems as lp porblem
                r1 = linprog(self.c, new_A_ub1, new_b_ub1, self.A_eq,
                             self.b_eq)
                r2 = linprog(self.c, new_A_ub2, new_b_ub2, self.A_eq,
                             self.b_eq)
                # add the subproblems into the queue, the better one first
                if not r1.success and r2.success:
                    self.Q.put((r2, new_A_ub2, new_b_ub2))
                elif not r2.success and r1.success:
                    self.Q.put((r1, new_A_ub1, new_b_ub1))
                elif r1.success and r2.success:
                    if -r1.fun > -r2.fun:                   # r1 is better
                        self.Q.put((r1, new_A_ub1, new_b_ub1))
                        self.Q.put((r2, new_A_ub2, new_b_ub2))
                    else:
                        self.Q.put((r2, new_A_ub2, new_b_ub2))
                        self.Q.put((r1, new_A_ub1, new_b_ub1))
 

def diet_problem():
    # get input data
    line_input = input()  # 1st line, get input as characters
    # nutrition of each type
    nutrition_sum = [-1 * int(i) for i in line_input.split()]
    line_input = input()
    food_types = int(line_input)  # 2nd line, types of food supplied
    food_price = []  # price of food in each type
    food_nutri = []  # nutritions of food in each type
    for i in range(food_types):  # following lines
        line_input = input()
        line = [-1 * int(i) for i in line_input.split()]
        food_price.append(-1 * line[-1])
        food_nutri.append(line[:-1])

    c = np.array(food_price)
    A_ub = np.array(food_nutri)
    A_ub = A_ub.T
    b_ub = np.array(nutrition_sum)

    # solver with simplex method
    solver = ILP(c, A_ub, b_ub)
    solver.solve()
    print(int(-solver.opt_val))
    for i, x in enumerate(solver.opt_x):
        if x:
            print(i, int(x))


if __name__ == '__main__':
    diet_problem()
