import QuantLib as ql
import math
from typing import Optional

from QuantLib.QuantLib import StochasticProcess
from . import ql_enums as qle, ql_utils as qlu, ql_conventions as qlc

def get_qlModel(model: qle.ShortRateModel,
                ts_handle: Optional[ql.QuantLib.YieldTermStructureHandle]=None,
                r0=0.05, 
                a=0.1, 
                b=0.05, 
                sigma=0.01, 
                lamda=0.0,
                eta=0.01, 
                rho=-0.75,
                volstepdates = None, 
                volatilities = None, 
                reversions = None):

    if model == qle.ShortRateModel.vasicek: 
        return ql.Vasicek(r0, a, b, sigma, lamda)
    elif model == qle.ShortRateModel.blackkarasinski:
        return ql.BlackKarasinski(ts_handle, a, sigma)
    elif model == qle.ShortRateModel.hullwhite:
        return ql.HullWhite(ts_handle, a, sigma)
    elif model == qle.ShortRateModel.gsr:
        return ql.Gsr(ts_handle, volstepdates, volatilities, reversions)
    elif model == qle.ShortRateModel.g2:
        return ql.G2(ts_handle, a, sigma, b, eta, rho) 
    else:
        return None


def qlShortRateModel(srmodel: qle.ShortRateModel,
                    yts_handle: ql.QuantLib.YieldTermStructureHandle,
                    **params):

    if srmodel == qle.ShortRateModel.vasicek: 
        return ql.Vasicek(params["r0"], params["a"], params["b"], params["sigma"], params["lamda"])
    elif srmodel == qle.ShortRateModel.blackkarasinski:
        return ql.BlackKarasinski(yts_handle, params["a"], params["sigma"])
    elif srmodel == qle.ShortRateModel.hullwhite:
        return ql.HullWhite(yts_handle, params["a"], params["sigma"])
    elif srmodel == qle.ShortRateModel.gsr:
        return ql.Gsr(yts_handle, params["volstepdates"], params["volatilities"], params["reversions"])
    elif srmodel == qle.ShortRateModel.g2:
        return ql.G2(yts_handle, params["a"], params["sigma"], params["b"], params["eta"], params["rho"]) 
    else:
        return None
    

def qlTreeCallableEngine(srmodel, gridpoints: int = 100):
    return ql.TreeCallableFixedRateBondEngine(srmodel, gridpoints)


def qlProcess(**params):

    process_name = params.get('name')

    if process_name is None:
        return None

    elif process_name == qle.StochasticProcess.geometric_brownian_motion:
        initial_value = params.get("initial_value")
        mu = params.get("mu")
        sigma = params.get("sigma")
        if initial_value and mu and sigma:
            return ql.GeometricBrownianMotionProcess(ql.QuoteHandle(ql.SimpleQuote(initial_value)), 
                                                    mu, 
                                                    sigma)
        else:
            return None
    
    elif process_name == qle.StochasticProcess.black_scholes:
        initial_value = params.get("initial_value")
        ts_ir = params.get("ts_ir")
        ts_vol = params.get("ts_vol")
        if initial_value and ts_ir and ts_vol:
            handle_ir = ql.YieldTermStructureHandle(ts_ir)
            handle_vol = ql.BlackVolTermStructureHandle(ts_vol)
            return ql.BlackScholesProcess(ql.QuoteHandle(ql.SimpleQuote(initial_value)), 
                                            handle_ir, 
                                            handle_vol)
        else:
            return None

    elif process_name == qle.StochasticProcess.black_scholes_merton:
        initial_value = params.get("initial_value")
        ts_ir = params.get("ts_ir")
        ts_vol = params.get("ts_vol")
        ts_div = params.get("ts_ir")
        if initial_value and ts_ir and ts_vol and ts_div:
            handle_ir = ql.YieldTermStructureHandle(ts_ir)
            handle_div = ql.YieldTermStructureHandle(ts_div)
            handle_vol = ql.BlackVolTermStructureHandle(ts_vol)
            return ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(initial_value)), 
                                                handle_div,
                                                handle_ir, 
                                                handle_vol)
        else:
            return None

    elif process_name == qle.StochasticProcess.generalized_black_scholes:
        initial_value = params.get("initial_value")
        ts_ir = params.get("ts_ir")
        ts_vol = params.get("ts_vol")
        ts_div = params.get("ts_div")
        if initial_value and ts_ir and ts_vol and ts_div:
            handle_ir = ql.YieldTermStructureHandle(ts_ir)
            handle_div = ql.YieldTermStructureHandle(ts_div)
            handle_vol = ql.BlackVolTermStructureHandle(ts_vol)
            return ql.GeneralizedBlackScholesProcess(ql.QuoteHandle(ql.SimpleQuote(initial_value)), 
                                                handle_div,
                                                handle_ir, 
                                                handle_vol)
        else:
            return None

    elif process_name == qle.StochasticProcess.extended_ornstein_uhlenbeck:
        speed = params.get("speed")
        sigma = params.get("sigma")
        x0 = params.get("x0")
        if speed and sigma and x0:
            return  ql.ExtendedOrnsteinUhlenbeckProcess(speed, 
                                                        sigma, 
                                                        x0, 
                                                        lambda x: x0)
        else:
            return None

    elif process_name == qle.StochasticProcess.ext_OU_with_jumps:
        speed = params.get("speed")
        sigma = params.get("sigma")
        x0 = params.get("x0")
        x1 = params.get("x1")
        beta = params.get("beta")
        eta = params.get("eta")
        jump_intensity = params('jump_intensity')
        if speed and sigma and x0 and x1 and beta and eta and jump_intensity:
            ou_process =  ql.ExtendedOrnsteinUhlenbeckProcess(speed, 
                                                        sigma, 
                                                        x0, 
                                                        lambda x: x0)
            return ql.ExtOUWithJumpsProcess(ou_process, 
                                            x1, 
                                            beta, 
                                            jump_intensity, 
                                            eta) 
        else:
            return None

    elif process_name == qle.StochasticProcess.black:
        initial_value = params.get("initial_value")
        ts_ir = params.get("ts_ir")
        ts_vol = params.get("ts_vol")
        
        if initial_value and ts_ir and ts_vol:
            handle_ir = ql.YieldTermStructureHandle(ts_ir)
            handle_vol = ql.YieldTermStructureHandle(ts_vol)
            return ql.BlackProcess(ql.QuoteHandle(ql.SimpleQuote(initial_value)), 
                                    handle_ir, 
                                    handle_vol)
        else:
            return None

    elif process_name == qle.StochasticProcess.merton76:
        initial_value = params.get("initial_value")
        sigma = params.get("sigma")
        jump_intensity = params.get("jump_intensity")
        yts_ir = params.get("yts_ir")
        yts_vol = params.get("yts_vol")
        yts_div = params.get("yts_div")
    
        if initial_value and yts_ir and yts_vol and yts_div and sigma:
            ytsh_ir = ql.YieldTermStructureHandle(yts_ir)
            ytsh_vol = ql.YieldTermStructureHandle(yts_vol)
            ytsh_div = ql.YieldTermStructureHandle(yts_div)
            qh_ji = ql.QuoteHandle(ql.SimpleQuote(jump_intensity))
            qh_jvol = ql.QuoteHandle(ql.SimpleQuote(sigma * \
                                                    math.sqrt(0.25 / qh_ji.value())))
            qh_mean = ql.QuoteHandle(ql.SimpleQuote(-qh_jvol.value()*qh_jvol.value()))
            qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(initial_value))
            return ql.Merton76Process(qh_ivalue, 
                                        ytsh_div, 
                                        ytsh_ir, 
                                        ytsh_vol, 
                                        qh_ji, 
                                        qh_mean, 
                                        qh_jvol)
        else:
            return None

    elif process_name == qle.StochasticProcess.variance_gamma:
        initial_value = params.get("initial_value")
        sigma = params.get("sigma")
        nu = params.get("nu")
        theta = params.get("theta")
        yts_ir = params.get("yts_ir")
        yts_div = params.get("yts_div")
    
        if initial_value and yts_ir and yts_div and nu and theta and sigma:
            ytsh_ir = ql.YieldTermStructureHandle(yts_ir)
            ytsh_div = ql.YieldTermStructureHandle(yts_div)
            qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(initial_value))
            return ql.VarianceGammaProcess(qh_ivalue, 
                                            ytsh_div,
                                            ytsh_ir, 
                                            sigma, 
                                            nu, 
                                            theta)
        else:
            return None

    elif process_name == qle.StochasticProcess.garmankohlagen:
        initial_value = params.get("initial_value")
        yts_ir_dom = params.get("yts_ir_dom")
        yts_ir_for = params.get("yts_ir_for")
        yts_vol = params.get("yts_vol")
    
        if initial_value and yts_ir_dom and yts_ir_for and yts_vol:
            ytsh_ir_dom = ql.YieldTermStructureHandle(yts_ir_dom)
            ytsh_ir_for = ql.YieldTermStructureHandle(yts_ir_for)
            ytsh_vol = ql.YieldTermStructureHandle(yts_vol)
            qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(initial_value))
            return ql.GarmanKohlagenProcess(qh_ivalue, 
                                            ytsh_ir_for, 
                                            ytsh_ir_dom, 
                                            ytsh_vol)
        else:
            return None

    elif process_name == qle.StochasticProcess.heston:
        initial_value = params.get("initial_value")
        yts_ir = params.get("yts_ir")
        yts_div = params.get("yts_div")
        v0 = params.get("v0")
        kappa = params.get("kappa")
        theta = params.get("theta")
        rho = params.get("rho")
        sigma = params.get("sigma")
    
        if initial_value and yts_ir and yts_div and v0 and kappa and theta and rho and sigma:
            ytsh_ir = ql.YieldTermStructureHandle(yts_ir)
            ytsh_div = ql.YieldTermStructureHandle(yts_div)
            qh_ivalue = ql.QuoteHandle(ql.SimpleQuote(initial_value))
            return ql.HestonProcess(ytsh_ir, 
                                    ytsh_div, 
                                    qh_ivalue, 
                                    v0, 
                                    kappa, 
                                    theta, 
                                    sigma, 
                                    rho)
        else:
            return None





def qlVolatility(**params):
    vol_model = params.get('name')

    if vol_model is None:
        return None

    elif vol_model == qle.VolatilityModel.black_constant_vol:
        value_date = params.get("value_date")
        volatility = params.get("volatility")
        day_count = params.get("day_count")
        qlcalendar = params.get("qlcalendar")
        if value_date and volatility and day_count and qlcalendar:
            vdate = qlu.datestr_to_qldate(value_date)
            qlday_count = qlc.ql_day_count[day_count]
            qlVol = ql.BlackConstantVol(vdate, qlcalendar, volatility, qlday_count)
            return qlVol
        else:
            return None

    elif vol_model == qle.VolatilityModel.black_variance_curve:
        value_date = params.get("value_date")
        expiries = params.get("expiries")
        volatilities = params.get("volatilities")
        day_count = params.get("day_count")

        if value_date and volatilities and expiries and day_count:
            vdate = qlu.datestr_to_qldate(value_date)
            qlday_count = qlc.ql_day_count[day_count]
            expiries = [qlu.datestr_to_qldate(expiry) for expiry in expiries]
            curve = ql.BlackVarianceCurve(vdate, expiries, volatilities, qlday_count)
            return curve
        else:
            return None

    elif vol_model == qle.VolatilityModel.black_variance_surface:
        value_date = params.get("value_date")
        qlcalendar = params.get("qlcalendar")
        day_count = params.get("day_count")
        vol_surface = params.get("vol_surface") # pymodels.VolSurface

        if value_date and qlcalendar and day_count and vol_surface:
            vdate = qlu.datestr_to_qldate(value_date)
            qlday_count = qlc.ql_day_count[day_count]
            surface = vol_surface.surface
            strikes = [surf.strike for surf in surface]
            vols = surface[0].vols
            expiries = [qlu.datestr_to_qldate(vol.date) for vol in vols]
            volMatrix = ql.Matrix(len(strikes), len(expiries))

            row = 0
            for surf in surface:
                col = 0
                for vol in surf.vols:
                    volMatrix[row][col] = vol.rate/100
                    col += 1
                row += 1
            
            volatilitySurface = ql.BlackVarianceSurface(
                            vdate,
                            qlcalendar,
                            expiries,
                            strikes,
                            volMatrix,
                            qlday_count
                            )
            volatilitySurface.enableExtrapolation()
            return volatilitySurface
        else:
            return None
    
    elif vol_model == qle.VolatilityModel.heston_black_vol_surface:
        spot_price = params.get("spot_price")
        heston_param = params.get("heston_param") # pymodels.HestonProcessParam
        yield_ts = params.get("yield_ts") #qlYTS
        dividend_ts = params.get("dividend_ts")#qlYTS
        if spot_price and heston_param and yield_ts and dividend_ts:
            yield_handle = ql.YieldTermStructureHandle(yield_ts)
            dividend_handle = ql.YieldTermStructureHandle(dividend_ts)
            spot_price = float(spot_price)
            process = ql.HestonProcess(yield_handle, 
                                        dividend_handle,
                                        ql.QuoteHandle(ql.SimpleQuote(spot_price)),
                                        heston_param.v0, 
                                        heston_param.kappa, 
                                        heston_param.theta, 
                                        heston_param.sigma, 
                                        heston_param.rho
                                        )
            hestonModel = ql.HestonModel(process)
            hestonHandle = ql.HestonModelHandle(hestonModel)
            hestonVolSurface = ql.HestonBlackVolSurface(hestonHandle)

            return hestonVolSurface
        else:
            return None
    else:
        return None







    







