import warnings
import os

warnings.filterwarnings("ignore")  # ignore warnings
import numpy as np
import copy
from operator import itemgetter
import numpy as np
import scipy.optimize
from scipy.spatial.distance import euclidean

import boss.utils.sobol_seq as sobol_seq
import multiprocessing

# Module-global name for the multiprocessing pool. We only create it once in
# Minimization.set_parallel()
process_pool = None


class Minimization:
    """
    Minimization utilities
    """

    @staticmethod
    def _run_minimizer(arguments):
        """
        Runs a single L-BFGS-B minimization starting from x0. Takes a single
        argument for easy compatibility with the multiprocessing library.

        arguments is a tuple containing
         func: The function to minimize. Must return value and gradients
         x0: Starting value
         bounds: Bounds passed to the minimizer
         args: arguments passed to the function func
        """
        func, x0, bounds, args = arguments
        x, f, d = scipy.optimize.fmin_l_bfgs_b(
            func,
            x0,
            bounds=bounds,
            args=args,
            factr=1e8,
            pgtol=1e-4,
            maxfun=1e4,
            maxiter=1e4,
            maxls=15,
        )
        rc = d["warnflag"] == 0
        return x, f, rc

    @staticmethod
    def _run_minimizer_with_finite_gradients(func, x0, bounds, args):
        """
        Runs a single L-BFGS-B minimization starting from x0
        Approximate gradients using finite difference

        func: The function to minimize. Must return value and gradients
        x0: Starting value
        bounds: Bounds passed to the minimizer
        args: arguments passed to the function func
        """
        x, f, d = scipy.optimize.fmin_l_bfgs_b(
            func,
            x0,
            bounds=bounds,
            args=args,
            factr=1e8,
            pgtol=1e-4,
            maxfun=1e4,
            maxiter=1e4,
            maxls=15,
            approx_grad=True,
        )
        rc = d["warnflag"] == 0
        return x, f, rc

    @staticmethod
    def set_parallel(num_procs):
        """ Set the number of parallel processes in the minimization step """
        global process_pool
        # Disable multithreading in the libraries scipy.optimize calls.
        # Seems these do not set it in the correct environment.
        # os.environ['OPENBLAS_NUM_THREADS'] = '1'
        # os.environ['MKL_NUM_THREADS'] = '1'
        # os.environ['OMP_NUM_THREADS'] = '1'

        # Create a multiprocessing pool
        if num_procs > 0:
            process_pool = multiprocessing.Pool(num_procs)

    @staticmethod
    def _minimize(arguments):
        """Wrapper on top of _run_minimizer for running either in parallel or
        in serial depending on whether a process pool has been created by
        Minimization.set_parallel().
        """
        if process_pool is not None:
            return_values = process_pool.map(Minimization._run_minimizer, arguments)
            minima = []
            for returned_tuple in return_values:
                x, f, s = returned_tuple
                if s:
                    minima.append([list(x), float(f)])
        else:
            minima = []
            for arg in arguments:
                x, f, s = Minimization._run_minimizer(arg)
                if s:
                    minima.append([list(x), float(f)])
        return minima

    @staticmethod
    def minimize(
        func,
        bounds,
        kerntype,
        acqs,
        min_dist_acqs,
        accuracy=0.3,
        args=(),
        lowest_min_only=True,
    ):
        """
        Tries to find global minimum of func by starting minimizers from
        accuracy*100 percentage of lowest acquisitions. func has to return both
        value and gradient given an x of same length as bounds.
        """
        acqsx = np.array(copy.deepcopy(acqs[:, : len(bounds)]))
        acqsy = np.array(copy.deepcopy(acqs[:, -1:]))

        points = []
        for i in range(len(acqsy)):
            points.append([list(acqsx[i]), float(acqsy[i])])

        points = Minimization._remove_duplicates(points, min_dist_acqs)
        points = sorted(points, key=itemgetter(1))
        X, Y = zip(*points)
        ind_last = min(len(Y) - 1, max(0, round(accuracy * (len(Y) - 1))))
        X = X[: ind_last + 1]
        X = np.array([X[i] for i in range(len(X))])

        widebounds = bounds.copy()
        p = np.array(kerntype) == "stdp"
        l = bounds[:, 1] - bounds[:, 0]
        widebounds[p, 0] -= 0.1 * l[p]
        widebounds[p, 1] += 0.1 * l[p]

        # Run bounded minimization on bounds which have been stretched for
        # periodic dimensions, then return the minima which have been found
        # inside the bounds. This prevents minima from being falsely
        # identified at the periodic boundaries.
        arguments = [(func, acq, widebounds, args) for acq in X]
        minima = Minimization._minimize(arguments)

        if len(minima) == 0:
            lo_acq = [list(acqsx[np.argmin(acqsy)]), float(np.min(acqsy))]
            minima.append(lo_acq)

        if lowest_min_only:
            globalmin = minima[0]
            for minimum in minima:
                if minimum[1] < globalmin[1]:
                    globalmin = minimum
            return globalmin
        else:
            minima = Minimization._remove_duplicates(minima, min_dist_acqs)
            return minima

    @staticmethod
    def minimize_from_sobol(
        func, bounds, num_pts, shift, args=(), lowest_min_only=True
    ):
        """
        Tries to find global minimum of func by starting minimizers from
        num_pts shifted sobol points. func has to return both
        value and gradient given an x of same length as bounds.
        """
        sobs = np.transpose(sobol_seq.i4_sobol_generate(len(bounds), num_pts, 1))

        points = []
        for i in range(len(sobs)):
            p = []
            for n in range(len(bounds)):
                bl = bounds[n][1] - bounds[n][0]
                p.append(bounds[n][0] + (sobs[i, n] * bl + shift[n]) % bl)
            points.append(p)

        arguments = [(func, pnt, bounds, args) for pnt in points]
        minima = Minimization._minimize(arguments)

        if len(minima) == 0:
            err_min = [list(points[-1]), float(func(points[-1], args[0], args[1])[0])]
            minima.append(err_min)  # later a better solution here?

        if lowest_min_only:
            globalmin = minima[0]
            for minimum in minima:
                if minimum[1] < globalmin[1]:
                    globalmin = minimum
            return globalmin
        else:
            return minima

    @staticmethod
    def minimize_from_random(
        func, bounds, num_pts, shift, args=(), lowest_min_only=True
    ):
        """
        Tries to find global minimum of func by starting minimizers from
        num_pts random points (min 10 max 100). func has to return both
        value and gradient given an x of same length as bounds.
        """
        if num_pts < 10:
            num_pts = 10
        elif num_pts > 100:
            num_pts = 100

        rands = np.random.random([num_pts, len(bounds)])

        points = []
        for i in range(len(rands)):
            p = []
            for n in range(len(bounds)):
                bl = bounds[n][1] - bounds[n][0]
                p.append(bounds[n][0] + rands[i, n] * bl)
            points.append(p)

        arguments = [(func, pnt, bounds, args) for pnt in points]
        minima = Minimization._minimize(arguments)

        if len(minima) == 0:
            err_min = [list(points[-1]), float(func(points[-1], args[0], args[1])[0])]
            minima.append(err_min)  # later a better solution here?

        if lowest_min_only:
            globalmin = minima[0]
            for minimum in minima:
                if minimum[1] < globalmin[1]:
                    globalmin = minimum
            return globalmin
        else:
            return minima

    @staticmethod
    def _remove_duplicates(original, min_distance):
        """
        Removes duplicates from a list of found local minima given a minimum
        distance between distinct minima.
        """
        if len(original) == 0:
            return original
        current = copy.deepcopy(original)
        next = []
        firstRef = current[0][0]
        first_encountered_times = 0
        while True:
            next = []
            ref = current[0][0]
            ref_f = current[0][1]
            if ref == firstRef:
                first_encountered_times += 1
                if first_encountered_times == 2:
                    break
            for i in range(1, len(current)):
                if euclidean(current[i][0], ref) > min_distance:
                    next.append(current[i])
            next.append([ref, ref_f])
            current = next
        return current
