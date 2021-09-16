import numba as nb

__all__ = ['SolverGeneric1ND_solve_data']

@nb.njit
def SolverGeneric1ND_solve_data(u, data, sol, naxes, is_zero_index):
    if u.ndim == 2:
        if naxes == 0:
            for i in range(u.shape[1]):
                if i == 0 and is_zero_index:
                    continue
                sol(u[:, i], data[i])

        elif naxes == 1:
            for i in range(u.shape[0]):
                if i == 0 and is_zero_index:
                    continue
                sol(u[i], data[i])

    elif u.ndim == 3:
        if naxes == 0:
            for i in range(u.shape[1]):
                for j in range(u.shape[2]):
                    if i == 0 and j == 0 and is_zero_index:
                        continue
                    sol(u[:, i, j], data[i, j])

        elif naxes == 1:
            for i in range(u.shape[0]):
                for j in range(u.shape[2]):
                    if i == 0 and j == 0 and is_zero_index:
                        continue
                    sol(u[i, :, j], data[i, j])

        elif naxes == 2:
            for i in range(u.shape[0]):
                for j in range(u.shape[1]):
                    if i == 0 and j == 0 and is_zero_index:
                        continue
                    sol(u[i, j, :], data[i, j])
    return u