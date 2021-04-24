import math


def exempt_milliwatts_sar(cm, ghz):
    """Calculate time-averaged power threshold for exemption, for radio
    frequency sources. (Exemption from routine RF exposure
    evaluation.) Note, this is only for UHF and part of SHF. Not
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
    if cm <= 20:
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
        (lambda f, r: 33450 * r ** 2 / f ** 2),  # How can that be? I don't know man, I didn't do it.
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
