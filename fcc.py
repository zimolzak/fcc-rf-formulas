# Adapted from original public domain BASIC by Wayne Overbeck N6NB, published 1996-2021. Compare to
# http://hintlink.com/power_density.htm by Paul Evans VP9KF. That page runs on public domain PHP by W4/VP9KF.
# Ultimate source is FCC OET Bulletin 65, Aug 1997.
# https://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet65/oet65.pdf

import math


def mpe_limits_cont_uncont_mwcm2(mhz):
    """Calculate MPE limit mW/cm^2 for controlled & uncontrolled
    environments, respectively. As a function of frequency in MHz.
    """
    if mhz <= 0:
        raise ValueError("frequency out of range: %s MHz" % str(mhz))
    elif mhz <= 1.34:
        return [100, 100]
    elif mhz < 3:
        return [100, 180 / (mhz ** 2)]
    elif mhz < 30:
        return [900 / (mhz ** 2), 180 / (mhz ** 2)]
    elif mhz < 300:
        return [1.0, 0.2]
    elif mhz < 1500:
        return [mhz / 300, mhz / 1500]
    elif mhz < 100000:
        return [5.0, 1.0]
    else:
        raise ValueError("frequency out of range: %s MHz" % str(mhz))


def compliant_distance_ft(gf, eirp_mw, mpe_limit_mwcm2):
    """Calculate compliant distance (ft) as function of effective
    radiated power (mW) as well as MPE limit and GF which includes
    ground reflection.
    """
    centimeters = math.sqrt(gf * eirp_mw / (4 * math.pi * mpe_limit_mwcm2))
    return centimeters / 30.48


def reflection_constant(ground_reflections):
    if type(ground_reflections) != bool:
        raise ValueError("ground_reflections must be boolean: %s" % str(ground_reflections))
    if not ground_reflections:
        return 1
    else:
        return 1.6 * 1.6  # source: OET #65 pp. 20-21. EPA 520/6-85-011.


def effective_isotropic_radiated_power(watts, t_average, duty, dbi):
    """Return value in milliwatts. watts is power seen at antenna feedpoint (*after* feedline loss). t_average and
    duty range 0 to 100. dbi is gain relative to isotropic. t_average is a characteristic of how much you operate (how
    much you hold the PTT). Duty factor is a characteristic of the mode (FM is always radiating when PTT,
    but SSB radiates only when you speak).
    """
    if not (0 <= t_average <= 100 and 0 <= duty <= 100):
        raise ValueError("t_average / duty out of range: %s / %s" % (str(t_average), str(duty)))
    milliwatts_average = 1000 * watts * (t_average / 100) * (duty / 100)
    return milliwatts_average * (10 ** (dbi / 10))


def is_good(watts, t_average, duty, dbi, ft, mhz, ground_reflections, controlled):
    """Return a boolean and a string."""
    meters = ft * 0.3048
    if is_exempt(watts, meters, mhz):  # fixme - might have to check power vs ERP vs EIRP
        return True, 'exemption'
    else:
        report = rf_evaluation_report(watts, t_average, duty, dbi, ft, mhz, ground_reflections)
        if controlled:
            return report["Compliant controlled"], 'evaluation'
        else:
            return report["Compliant uncontrolled"], 'evaluation'


def rf_evaluation_report(watts, t_average, duty, dbi, ft, mhz, ground_reflections):
    """Report on power density (mW/cm^2) given input power and distance; and on compliant distances (controlled &
    uncontrolled environment) given input power. Return a dict.
    """
    eirp = effective_isotropic_radiated_power(watts, t_average, duty, dbi)
    s = power_density_mwcm2(eirp, ft, ground_reflections)
    limit_controlled, limit_uncontrolled = mpe_limits_cont_uncont_mwcm2(mhz)  # mW/cm^2
    feet_controlled = compliant_distance_ft(reflection_constant(ground_reflections), eirp, limit_controlled)
    feet_uncontrolled = compliant_distance_ft(reflection_constant(ground_reflections), eirp, limit_uncontrolled)
    compliant_controlled = s < limit_controlled
    compliant_uncontrolled = s < limit_uncontrolled
    return {"Power density": s,
            "MPE controlled": limit_controlled,
            "MPE uncontrolled": limit_uncontrolled,
            "Distance controlled": feet_controlled,
            "Distance uncontrolled": feet_uncontrolled,
            "Compliant controlled": compliant_controlled,
            "Compliant uncontrolled": compliant_uncontrolled}


def power_density_mwcm2(eirp_mw, ft, ground_reflections):
    """Calculate power density (mW/cm^2) given input power (mW) and distance"""
    cm = ft * 30.48
    return reflection_constant(ground_reflections) * eirp_mw / (4 * math.pi * (cm ** 2))


def exempt_watts_generic(meters, mhz):
    """Try SAR and MPE method, return best threshold (float) and method (str)."""
    try:
        p_th = exempt_milliwatts_sar(meters * 100, mhz / 1000) / 1000
    except ValueError:
        return exempt_watts_mpe(meters, mhz), 'MPE'
        # That func will raise exception again if mhz still out of range.
    try:
        erp_th = exempt_watts_mpe(meters, mhz)
    except ValueError:
        return p_th, 'SAR'
    if p_th > erp_th:
        return p_th, 'SAR wins'
    else:
        return erp_th, 'MPE wins'


def is_exempt(watts, meters, mhz):
    """Return boolean."""
    try:
        threshold, method = exempt_watts_generic(meters, mhz)
        return watts < threshold  # fixme - consider returning tuple of (True, method)
    except RFEvaluationError:
        return False
    # Do not catch general ValueError, which means mhz may be out of range.


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


class RFEvaluationError(ValueError):
    pass


def exempt_watts_mpe(meters, mhz):
    """Calculate the effective radiated power threshold for exemption, for
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
        evaluation_message = "R < L/2pi (%s < %s m). RF evaluation required."
        raise RFEvaluationError(evaluation_message % (str(meters), l_str))
    for i in range(len(cutpoints)):
        if i == len(cutpoints) - 1:
            raise ValueError("frequency out of range: %s MHz" % str(mhz))
        f_low = cutpoints[i]
        f_high = cutpoints[i + 1]
        if f_low <= mhz < f_high:
            return functions[i](mhz, meters)
