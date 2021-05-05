import math


def stds(f):  # fixme - how does this relate to mpe_power_density_mwcm2
    if f < 1.34:
        return [100, 100]
    elif f < 3:
        return [100, 180 / ((f) ** 2)]
    elif f < 30:
        return [900 / ((f) ** 2), 180 / ((f) ** 2 )]
    elif f < 300:
        return [1.0, 0.2]
    elif f < 1500:
        return [f / 300, f / 1500]
    elif f < 100000:
        return [5.0, 1.0]
    else:
        raise ValueError


def transform_dx(gf, eirp, std1):
    dx1 = math.sqrt((gf * eirp) / (std1 * math.pi))
    dx1 = dx1 / 30.48
    dx1 = (int((dx1 * 10) + 0.5)) / 10
    return dx1


def power_density_antenna(wattsorg, tavg, duty, gain, ft, f, g):
    """Adapted from orig public domain by Wayne Overbeck N6Nb, 1996-2021.
    tavg and duty range 0 to 100. gain in dBi, f is freq in MHz, g is
    'y' or 'n'.
    """
    watts = wattsorg * (tavg / 100)
    watts = watts * (duty / 100)
    pwr = 1000 * watts
    eirp = pwr * (10 ** (gain / 10))
    dx = ft * 30.48  # centimeters
    std1, std2 = stds(f)
    if g == "n":
        gf = 0.25
        gr = "without"
    elif g == "y":
        gf = 0.64
        gr = "with"
    else:
        raise ValueError
    pwrdens = gf * eirp / (math.pi * (dx ** 2))
    pwrdens = (int((pwrdens * 10000) + 0.5)) / 10000  # your mW/cm2 at given dist
    dx1 = transform_dx(gf, eirp, std1)  # compliant distances in feet
    dx2 = transform_dx(gf, eirp, std2)
    std1 = (int((std1 * 100) + 0.5)) / 100  # these are MPE limits mw/cm2
    std2 = (int((std2 * 100) + 0.5)) / 100  # FIXME - this is really just rounding
    return [pwrdens, dx1, dx2, std1, std2, gr]


def mpe_power_density_mwcm2(mhz, controlled):
    """Max allowed MPE specified in mW/cm^2."""
    if type(controlled) != bool:
        raise ValueError("value of 'controlled' must be boolean: %s" % str(controlled))
    if controlled:
        if 10 <= mhz <= 300:
            return 1.0
        elif 300 < mhz <= 1500:
            return mhz / 300
        elif 1500 < mhz <= 100000:
            return 5.0
        else:
            raise ValueError("frequency out of range: %s \MHz" % str(mhz))
    else:
        if 10 <= mhz <= 300:
            return 0.2
        elif 300 < mhz <= 1500:
            return mhz / 1500
        elif 1500 < mhz <= 100000:
            return 1.0
        else:
            raise ValueError("frequency out of range: %s \MHz" % str(mhz))


def exempt_watts_generic(meters, mhz):
    """Try SAR and MPE method, return best threshold and method."""
    try:
        p_th = exempt_milliwatts_sar(meters * 100, mhz / 1000) / 1000
    except ValueError:
        return (exempt_watts_mpe(meters, mhz), 'MPE')  # raises again if still out of range
    try:
        erp_th = exempt_watts_mpe(meters, mhz)
    except ValueError:
        return (p_th, 'SAR')
    if p_th > erp_th:
        return (p_th, 'SAR wins')
    else:
        return(erp_th, 'MPE wins')


def exempt_milliwatts_sar(cm, ghz):
    """Calculate time-averaged power threshold for exemption, for radio
    frequency sources. (Exemption from routine RF exposure
    evaluation.) Note: this is only for UHF, and part of SHF. Not
    applicable to VHF, HF, and frequencies below. FCC formula is
    'based on localized specific absorption rate (SAR) limits.' For
    lower frequencies, you need to look at MPE-based exemption with
    ERP threshold, not SAR-based.

    cm is the distance, ghz is the frequency. Return value in mW.
    Source: FCC 19-126 p.23

    """
    if 0.3 <= ghz < 1.5:
        erp20 = 2040 * ghz
    elif 1.5 <= ghz <= 6:
        erp20 = 3060
    else:
        raise ValueError("frequency out of range: %s GHz" % str(ghz))
    x = -1 * math.log10(60 / (erp20 * math.sqrt(ghz)))
    if 0 <= cm <= 20:
        p_threshold = erp20 * (cm / 20) ** x
    elif 20 < cm <= 40:
        p_threshold = erp20
    else:
        raise ValueError("distance out of range: %s cm" % str(cm))
    return p_threshold


def exempt_watts_mpe(meters, mhz):
    """Calculate the Effective Radiated Power threshold for exemption, for
    radio frequency sources, using the MPE method. Formulas based on
    FCC 19-126, Table 2, p. 26.

    meters is the distance, mhz is the frequency, return val is in watts.
    """
    cutpoints = [0.3, 1.34, 30, 300, 1500, 100000]
    functions = [
        (lambda f, r: 1920 * r ** 2),
        (lambda f, r: 3450 * r ** 2 / f ** 2),
        (lambda f, r: 3.83 * r ** 2),
        (lambda f, r: 0.0128 * r ** 2 * f),
        (lambda f, r: 19.2 * r ** 2)
    ]
    c = 299792458  # m/s
    nu = mhz * 1E6  # Hz
    l_over_2pi = c / nu / (2 * math.pi)  # m
    if meters < l_over_2pi:
        l_str = str(round(l_over_2pi))
        raise ValueError("R < L/2pi (%s < %s m). RF evaluation required." % (str(meters), l_str))
    for i in range(len(cutpoints)):
        if i == len(cutpoints) - 1:
            raise ValueError("frequency out of range: %s MHz" % str(mhz))
        f_low = cutpoints[i]
        f_high = cutpoints[i + 1]
        if f_low <= mhz < f_high:
            return functions[i](mhz, meters)
