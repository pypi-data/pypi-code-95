import QuantLib as ql
import math


# Geometric Brownian Motion
class SP_GBM:
    def __init__(self, initial_value: float, mu: float, sigma: float):
        self.__initial_value = initial_value
        self.__mu = mu
        self.__sigma = sigma

    def qlProcess(self):
        
        return ql.GeometricBrownianMotionProcess(self.__initial_value, 
                                                self.__mu, 
                                                self.__sigma)


# Black Scholes 
class SP_BS:
    def __init__(self, initial_value: float, 
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    bvtsh_vol: ql.QuantLib.BlackVolTermStructureHandle):
        self.__initial_value = initial_value
        self.__ytsh_ir = ytsh_ir # interest rate term stucture
        self.__bvtsh_vol = bvtsh_vol # blak vol term structure

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return  ql.BlackScholesProcess(qh_ivalue, 
                                        self.__ytsh_ir, 
                                        self.__bvtsh_vol)

# Black Scholes Merton
class SP_BSM:
    def __init__(self, initial_value: float, 
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    ytsh_div: ql.QuantLib.YieldTermStructureHandle, 
                    bvtsh_vol: ql.QuantLib.BlackVolTermStructureHandle):
        self.__initial_value = initial_value
        self.__ytsh_ir = ytsh_ir #interest rate term structure
        self.__ytsh_div = ytsh_div  # dividend term structure
        self.__bvtsh_vol = bvtsh_vol # black volatility term structure

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return  ql.BlackScholesMertonProcess(qh_ivalue, 
                                                self.__ytsh_div, 
                                                self.__ytsh_ir , 
                                                self.__bvtsh_vol)

# Generalised Black Scholes
class SP_GBS:
    def __init__(self, initial_value: float, 
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    ytsh_div: ql.QuantLib.YieldTermStructureHandle, 
                    bvtsh_vol: ql.QuantLib.BlackVolTermStructureHandle):
        self.__initial_value = initial_value
        self.__ytsh_ir = ytsh_ir #interest rate term structure
        self.__ytsh_div = ytsh_div  # dividend term structure
        self.__bvtsh_vol = bvtsh_vol # black volatility term structure


    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return  ql.GeneralizedBlackScholesProcess(qh_ivalue, 
                                                self.__ytsh_div, 
                                                self.__ytsh_ir , 
                                                self.__bvtsh_vol)

#Extended Ornstein Uhlenbeck
class SP_EOU:
    def __init__(self, x0: float, speed: float, sigma: float):
        self.__x0 = x0
        self.__speed = speed
        self.__sigma = sigma  

    def qlProcess(self):
        return ql.ExtendedOrnsteinUhlenbeckProcess(self.__speed, 
                                                    self.__sigma, 
                                                    self.__x0, 
                                                    lambda x: self.__x0)

#Extended Ornstein Uhlenbeck with Jump Process
class SP_EOUJump:
    def __init__(self, x0: float, speed: float, sigma: float,
                x1: float, beta: float, eta: float, jump_intensity: float):
        self.__x0 = x0
        self.__speed = speed
        self.__sigma = sigma  
        self.__x1 = x1
        self.__beta = beta  
        self.__eta = eta
        self.__jump_intensity = jump_intensity

    def qlProcess(self):
        ouProcess = ql.ExtendedOrnsteinUhlenbeckProcess(self.__speed, 
                                                    self.__sigma, 
                                                    self.__x0, 
                                                    lambda x: self.__x0)
        return ql.ExtOUWithJumpsProcess(ouProcess, 
                                        self.__x1, 
                                        self.__beta, 
                                        self.__jump_intensity, 
                                        self.__eta)

# Black
class SP_Black:
    def __init__(self, initial_value: float, 
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    bvtsh_vol: ql.QuantLib.BlackVolTermStructureHandle):
        self.__initial_value = initial_value
        self.__ytsh_ir = ytsh_ir # interest rate term stucture
        self.__bvtsh_vol = bvtsh_vol # blak vol term structure

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return  ql.BlackScholesProcess(qh_ivalue, 
                                        self.__ytsh_ir, 
                                        self.__bvtsh_vol)


# Merton 76
class SP_M76:
    def __init__(self, initial_value: float, 
                    sigma: float,
                    jump_intensity: float,
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    bvtsh_vol: ql.QuantLib.BlackVolTermStructureHandle,
                    ytsh_div: ql.QuantLib.YieldTermStructureHandle):
        self.__initial_value = initial_value
        self.__sigma = sigma
        self.__jump_intensity = jump_intensity
        self.__ytsh_ir = ytsh_ir # interest rate term stucture
        self.__bvtsh_vol = bvtsh_vol # black vol term structure
        self.__ytsh_div = ytsh_div # dividend term structure

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        qh_jintensity = ql.QuoteHandle(ql.SimpleQuote(self.__jump_intensity))
        qh_jvolatility = ql.QuoteHandle(ql.SimpleQuote(self.__sigma * \
                                        math.sqrt(0.25 / qh_jintensity.value())))
        qh_mean = ql.QuoteHandle(ql.SimpleQuote(-qh_jvolatility.value() * \
                                                qh_jvolatility.value()))
        return  ql.Merton76Process(qh_ivalue, 
                                    self.__ytsh_div, 
                                    self.__ytsh_ir, 
                                    self.__bvtsh_vol, 
                                    qh_jintensity, 
                                    qh_mean, 
                                    qh_jvolatility)


# Variance Gamma
class SP_VG:
    def __init__(self, initial_value: float, 
                    sigma: float,
                    nu: float,
                    theta: float,
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    ytsh_div: ql.QuantLib.YieldTermStructureHandle):
        self.__initial_value = initial_value
        self.__sigma = sigma
        self.__nu = nu
        self.__theta = theta
        self.__ytsh_ir = ytsh_ir # interest rate term stucture
        self.__ytsh_div = ytsh_div # dividend term structure

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return ql.VarianceGammaProcess(qh_ivalue, 
                                        self.__ytsh_div, 
                                        self.__ytsh_ir, 
                                        self.__sigma, 
                                        self.__nu, 
                                        self.__theta)


# Garman Kolhagen
class SP_GK:
    def __init__(self, initial_value: float, 
                    ytsh_ir_dom: ql.QuantLib.YieldTermStructureHandle, 
                    ytsh_ir_for: ql.QuantLib.YieldTermStructureHandle,
                    bvtsh_vol: ql.QuantLib.BlackVolTermStructureHandle):
        self.__initial_value = initial_value
        
        self.__ytsh_ir_dom = ytsh_ir_dom # domestic interest rate term stucture
        self.__ytsh_ir_for = ytsh_ir_for # foreign interest rate term stucture
        self.__bvtsh_vol = bvtsh_vol # volatility rate term stucture

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return ql.GarmanKohlagenProcess(qh_ivalue, 
                                        self.__ytsh_ir_for, 
                                        self.__ytsh_ir_dom, 
                                        self.__bvtsh_vol)


# Heston
class SP_Heston:
    def __init__(self, initial_value: float, 
                    v0: float, 
                    kappa: float, 
                    theta: float, 
                    sigma: float, 
                    rho: float,
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle, 
                    ytsh_div: ql.QuantLib.YieldTermStructureHandle):
        self.__initial_value = initial_value
        self.__v0 = v0
        self.__kappa = kappa
        self.__theta = theta
        self.__sigma = sigma
        self.__rho = rho
        self.__ytsh_ir = ytsh_ir # domestic interest rate term stucture
        self.__ytsh_div = ytsh_div # dividend term stucture
        

    def qlProcess(self):
        qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(self.__initial_value))
        return ql.HestonProcess(self.__ytsh_ir, 
                                self.__ytsh_div, 
                                qh_ivalue, 
                                self.__v0, 
                                self.__kappa, 
                                self.__theta, 
                                self.__sigma, 
                                self.__rho)


# Hull White
class SP_HW:
    def __init__(self, a: float,  
                    sigma: float, 
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle):
        self.__a = a
        self.__sigma = sigma
        self.__ytsh_ir = ytsh_ir # domestic interest rate term stucture
        

    def qlProcess(self):
        return ql.HullWhiteProcess(self.__ytsh_ir, 
                                    self.__a, 
                                    self.__sigma)


# Hull White
class SP_HWF:
    def __init__(self, a: float,  
                    sigma: float, 
                    ytsh_ir: ql.QuantLib.YieldTermStructureHandle):
        self.__a = a
        self.__sigma = sigma
        self.__ytsh_ir = ytsh_ir # domestic interest rate term stucture
        

    def qlProcess(self):
        return ql.HullWhiteForwardProcess(self.__ytsh_ir, 
                                    self.__a, 
                                    self.__sigma)