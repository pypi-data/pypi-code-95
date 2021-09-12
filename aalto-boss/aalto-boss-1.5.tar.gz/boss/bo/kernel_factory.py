import GPy


class KernelFactory:
    """
    This class contains the construction of the kernel.
    """

    @staticmethod
    def construct_kernel(settings, forced_hypers=None):
        """
        Creates the kernel.
        """
        kerns = [None] * (settings.dim)
        KernelFactory._select_kernels(kerns, settings, forced_hypers)
        if forced_hypers is None:
            KernelFactory._set_constraints(kerns, settings)
        if forced_hypers is None:
            KernelFactory._set_priors(kerns, settings)

        # multiplies the kernels into one object and returns it
        Kernel = kerns[0]
        if len(kerns) > 1:
            for i in range(1, len(kerns)):
                Kernel = Kernel * kerns[i]
        return Kernel

    @staticmethod
    def _select_kernels(kerns, settings, forced_hypers):
        """
        Selects and creates kernel objects for each dimension. Hyperparameters
        are set to their initial values and default constraints removed.
        """
        for i in range(settings.dim):
            if forced_hypers is None:
                if i == 0:
                    ksi = settings["thetainit"][0]
                else:
                    ksi = 1.0
                klsi = settings["thetainit"][i + 1]
            else:
                ksi = forced_hypers[0]
                klsi = forced_hypers[1 + i]
            kper = settings["periods"][i]

            ktype = settings["kernel"][i]
            if ktype == "stdp":
                kerns[i] = GPy.kern.StdPeriodic(
                    input_dim=1,
                    variance=ksi,
                    period=kper,
                    lengthscale=klsi,
                    ARD1=True,
                    ARD2=True,
                    active_dims=[i],
                    name="kern",
                )
            elif ktype == "rbf":
                kerns[i] = GPy.kern.RBF(
                    input_dim=1,
                    variance=ksi,
                    lengthscale=klsi,
                    ARD=True,
                    active_dims=[i],
                    name="kern",
                )
            elif ktype == "mat32":
                kerns[i] = GPy.kern.Matern32(
                    input_dim=1,
                    variance=ksi,
                    lengthscale=klsi,
                    ARD=True,
                    active_dims=[i],
                    name="kern",
                )
            elif ktype == "mat52":
                kerns[i] = GPy.kern.Matern52(
                    input_dim=1,
                    variance=ksi,
                    lengthscale=klsi,
                    ARD=True,
                    active_dims=[i],
                    name="kern",
                )
            else:
                raise TypeError(f"""Unknown kernel {settings['kernel'][i]}""")

    #            kerns[i].unconstrain()

    @staticmethod
    def _set_constraints(kerns, settings):
        """
        Sets hyperparameter constraints on kernels.
        """
        # variance
        if settings["thetabounds"] is not None:
            kerns[0].variance.constrain_bounded(
                settings["thetabounds"][0][0],
                settings["thetabounds"][0][1],
                warning=False,
            )
            # lengthscale
            for i in range(settings.dim):
                kerns[i].lengthscale.constrain_bounded(
                    settings["thetabounds"][i + 1][0],
                    settings["thetabounds"][i + 1][1],
                    warning=False,
                )
        # period
        for i in range(settings.dim):
            if settings["kernel"][i] == "stdp":  # pbc
                kerns[i].period.constrain_fixed(settings["periods"][i], warning=False)

        # other than the first kernel's variances
        if settings.dim > 1:
            for i in range(1, settings.dim):
                kerns[i].variance.constrain_fixed(1.0, warning=False)

    @staticmethod
    def _set_priors(kerns, settings):
        """
        Sets hyperparameter priors on kernels.
        """
        if settings["thetaprior"] is not None:
            prior = None
            if settings["thetaprior"] == "gamma":
                prior = GPy.priors.Gamma
            else:
                raise TypeError(
                    "Unknown value '"
                    + settings["thetaprior"]
                    + "' given in keyword thetaprior."
                )

            # variance
            kerns[0].variance.set_prior(
                prior(settings["thetapriorpar"][0][0], settings["thetapriorpar"][0][1]),
                warning=False,
            )
            # lengthscale
            for i in range(settings.dim):
                kerns[i].lengthscale.set_prior(
                    prior(
                        settings["thetapriorpar"][i + 1][0],
                        settings["thetapriorpar"][i + 1][1],
                    ),
                    warning=False,
                )
