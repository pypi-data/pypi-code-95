import units_QBD
from math import sqrt

def eigenvalues_1(space__grid, energy__grid, mass__grid, level__resolution=0.001):
    interval = space__grid[1] - space__grid[0]
    as2 = 2.0 * units_QBD.M_E[0] * units_QBD.E[0] * interval * interval / units_QBD.H__BAR[0] / units_QBD.H__BAR[0]
 
    grid__points__count = len(space__grid)

    AZW_D = [0]
    AZW_U = [0]
    for i in range(1, grid__points__count - 1):
        value =  energy__grid[i] * as2 + 2.0 / (mass__grid[i - 1] + mass__grid[i]) + 2.0 / (mass__grid[i + 1] + mass__grid[i])
        AZW_D.append(value)
        AZW_U.append(-2.0 / (mass__grid[i + 1] + mass__grid[i]))
    AZW_D.append(0)
    AZW_U.append(0)

    
    eigenvalues = []
    level = 2
    while(True):
        E_min = min(energy__grid)
        E_max = max(energy__grid)
        E_ave = ...

        while E_max - E_min > level__resolution:
            E_ave = (E_max + E_min) / 2
            eta = 0
            u = AZW_D[1] - E_ave * as2
            if u < 0: eta += 1
            for i in range(2, grid__points__count):
                u = AZW_D[i] - E_ave * as2 - AZW_U[i-1] * AZW_U[i-1] / u
                if u < 0: eta += 1

            if eta < level:   
                E_min = E_ave
            else:                           
                E_max = E_ave

        eigenvalues.append(E_ave / units_QBD.SI_['eV'][0])
        level +=1

        if len(eigenvalues) > 1:
            if eigenvalues[-2] == eigenvalues[-1]: 
                break

    return eigenvalues[:-2]

def eigenfunctions_1(space__grid, energy__grid, mass__grid, energy):
    interval = space__grid[1] - space__grid[0]
    as2 = 2.0 * units_QBD.M_E[0] * units_QBD.E[0] * interval * interval / units_QBD.H__BAR[0] / units_QBD.H__BAR[0]
 
    grid__points__count = len(space__grid)

    AZW_D = [0]
    AZW_U = [0]
    for i in range(1, grid__points__count - 1):
        value =  energy__grid[i] * as2 + 2.0 / (mass__grid[i - 1] + mass__grid[i]) + 2.0 / (mass__grid[i + 1] + mass__grid[i])
        AZW_D.append(value)
        AZW_U.append(-2.0 / (mass__grid[i + 1] + mass__grid[i]))
    AZW_D.append(0)
    AZW_U.append(0)

    ThetaM = [0]
    ThetaM.append(1. / (AZW_D[1] - energy * as2))
    for i in range(2,grid__points__count):
        ThetaM.append(1 / (AZW_D[i] - energy * as2 - AZW_U[i - 1] * AZW_U[i - 1] * ThetaM[i - 1]))

    ThetaP = [0] * grid__points__count
    for i in range(2, grid__points__count):
        i = grid__points__count - i
        ThetaP[i] = 1 / (AZW_D[i] - energy * as2 - AZW_U[i] * AZW_U[i] * ThetaP[i + 1])
    ThetaP[-1] = 1. / (AZW_D[-1] - energy * as2)

    wave__vector = [0] * grid__points__count
    k = grid__points__count / 2

    for i in range(int(k) + 1, grid__points__count):
        wave__vector[i] = -AZW_U[i - 1] * ThetaP[i] * wave__vector[i - 1]

    wave__vector[int(k)] = 1

    for i in range(1, int(k)):
        i = int(k) - i
        wave__vector[i] = -AZW_U[i] * ThetaM[i] * wave__vector[i + 1]


    for i in range(1, grid__points__count):
        if abs(wave__vector[int(k)]) < abs(wave__vector[i]): k = i



    for i in range(int(k) + 1, grid__points__count):
        wave__vector[i] = -AZW_U[i - 1] * ThetaP[i] * wave__vector[i - 1]

    wave__vector[int(k)] = 1

    for i in range(1, int(k)):
        i = int(k) - i
        wave__vector[i] = -AZW_U[i] * ThetaM[i] * wave__vector[i + 1]

    
    Norma = 0.

    for i in range(1, grid__points__count): 
        Norma += wave__vector[i] * wave__vector[i]
    Norma *= interval

    for i in range(1, grid__points__count):
        wave__vector[i] /= sqrt(Norma)

    return wave__vector