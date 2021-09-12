from itertools import repeat
from multiprocessing import Pool


class HMCwrapper:
    def __init__(self, sample):
        self.sample = sample

    def averageacq(self, acqfunc, nprocs):
        def wrapped(x, model, params):
            """
            Evaluate acqfn with all params in HMC-sample using multiprocessing
            """
            # get acq values for the sample
            param = model.get_unfixed_params()
            f_acqu = np.atleast_2d(np.array([0.0]))
            scipygradient = np.atleast_2d(np.zeros(x.shape)).T
            chunks = [
                self.sample[
                    i::nprocs,
                ]
                for i in range(nprocs)
            ]
            pool = Pool(processes=nprocs)
            results = pool.map(
                self.g,
                zip(chunks, repeat(x), repeat(model), repeat(params), repeat(acqfunc)),
            )
            pool.close()
            for procres in results:
                for iterres in procres:
                    f, g = iterres
                    f_acqu += f
                    scipygradient += g
            # reset model to starting state
            model.set_unfixed_params(param)
            # average over the sample and return
            n = self.sample.shape[0]
            return f_acqu / n, np.asfortranarray(scipygradient / n)

        return wrapped

    def g(self, zipped):
        chunk, x, model, params, acqfunc = zipped
        res = []
        for p in chunk:
            model.set_unfixed_params(p)
            res.append(acqfunc(x, model, params))
        return res
