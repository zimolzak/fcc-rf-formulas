# Adapted from original public domain BASIC by Wayne Overbeck N6NB, published 1996-2021.
# http://n6nb.com/rfsafetybasic.PDF . Compare to http://hintlink.com/power_density.htm by Paul Evans VP9KF. That page
# runs on public domain PHP by W4/VP9KF. Ultimate source is FCC OET Bulletin 65, Aug 1997.
# https://transition.fcc.gov/Bureaus/Engineering_Technology/Documents/bulletins/oet65/oet65.pdf

import math

CM_PER_FT = 30.48
M_PER_FT = CM_PER_FT / 100


class PoweredAntenna:
    """Structure for representing an antenna with a certain gain, operating characteristics, and feed power"""

    def __init__(self, watts: float, t_average: float, duty: float, dbi: float):
        """
        :param watts: Power seen at antenna feedpoint (*after* feedline loss)
        :param t_average: Ranges 0 to 100, characteristic of how much you operate
        :param duty: Ranges 0 to 100, characteristic of the mode such as FM vs SSB
        :param dbi: Gain relative to isotropic (decibels)
        """
        self.watts = watts
        self.t_average = t_average
        self.duty = duty
        self.dbi = dbi


class RFEvaluationReport:
    """Perform an RF evaluation of antenna/mode setup. Determine power density (mW/cm^2) given input power and distance,
    allowed power density, and compliant distances (controlled & uncontrolled environment)."""
    def __init__(self, antenna: PoweredAntenna, ft: float, mhz: float, ground_reflections: bool):
        """
        :param antenna:
        :param ft: Distance from center of ANT to area of interest (feet)
        :param mhz: Frequency of RF radiation, (megahertz)
        :param ground_reflections: Whether to account for radiation coming from ground reflections
        """
        self.antenna = antenna
        self.ft = ft
        self.mhz = mhz
        self.ground_reflections = ground_reflections
        # Calculations
        self.eirp = effective_isotropic_radiated_power(antenna)
        self.power_density = power_density_mwcm2(self.eirp, ft, ground_reflections)
        self.power_density_c, self.power_density_u = mpe_limits_cont_uncont_mwcm2(mhz)  # mW/cm^2
        k = reflection_constant(ground_reflections)
        self.ft_c = compliant_distance_ft(k, self.eirp, self.power_density_c)
        self.ft_u = compliant_distance_ft(k, self.eirp, self.power_density_u)
        self.compliant_c = self.power_density < self.power_density_c
        self.compliant_u = self.power_density < self.power_density_u
        self._calculation_list = (self.power_density, self.power_density_c, self.power_density_u, self.ft_c, self.ft_u,
                                  self.compliant_c, self.compliant_u)  # tuple in specific order, for testing

    def __str__(self):
        return """Power density (mW/cm^2): %s
MPE controlled (mW/cm^2): %s
MPE uncontrolled (mW/cm^2): %s
Distance controlled (ft): %s
Distance uncontrolled (ft): %s
Compliant controlled: %s
Compliant uncontrolled: %s""" % self._calculation_list


def is_compliant(antenna, ft, mhz, ground_reflections, controlled):
    """Determine whether a given combination of (antenna, power, frequency, distance) is compliant in general, by a
    complete trial of methods. Either uses SAR exemption, MPE exemption, or evaluation.

    :param PoweredAntenna antenna:
    :param float ft: Distance from center of ANT to area of interest (feet)
    :param float mhz: Frequency of RF radiation (megahertz)
    :param bool ground_reflections: Whether to account for radiation coming from ground reflections
    :param bool controlled: Whether the area of interest is controlled (occupational) or uncontrolled (public)
    :return: A (bool, str) tuple of whether the setup is compliant, and a string describing the method used
    :rtype: tuple
    """
    meters = ft * M_PER_FT
    ex, method = is_exempt(antenna.watts, meters, mhz)  # fixme - might have to check power vs ERP vs EIRP
    if ex:
        return True, method
    else:
        report = RFEvaluationReport(antenna, ft, mhz, ground_reflections)
        if controlled:
            return report.compliant_c, 'evaluation'
        else:
            return report.compliant_u, 'evaluation'


# Evaluation functions ########


def mpe_limits_cont_uncont_mwcm2(mhz):
    """Determine maximum permissible exposure limits for RF, from FCC references.

    :param float mhz: The radio frequency of interest (megahertz)
    :return: MPE limits (mW/cm^2) for controlled & uncontrolled environments, respectively
    :rtype: list
    :raises ValueError: if mhz is out of range (cannot be found in the FCC lookup table)
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
    """Calculate what distance from an antenna will comply with a maximum permissible exposure (power density) limit.
    Based on area of sphere.

    :param float gf: A factor determining how much the RF is increased by ground reflections
    :param float eirp_mw: Effective isotropic radiated power of the antenna (milliwatts)
    :param float mpe_limit_mwcm2: MPE limit (milliwatts per square centimeter)
    :return: Compliant distance from antenna (feet)
    :rtype: float
    """
    centimeters = math.sqrt(gf * eirp_mw / (4 * math.pi * mpe_limit_mwcm2))
    return centimeters / CM_PER_FT


def power_density_mwcm2(eirp_mw, ft, ground_reflections):
    """Calculate power density at a certain distance from an antenna. Based on area of sphere.

    :param float eirp_mw: Effective isotropic radiated power of the antenna (milliwatts)
    :param float ft: Distance from antenna (feet)
    :param bool ground_reflections: Whether to account for ground reflections
    :return: Power density (milliwatts per square centimeter)
    :rtype: float
    """
    cm = ft * CM_PER_FT
    return reflection_constant(ground_reflections) * eirp_mw / (4 * math.pi * (cm ** 2))


def reflection_constant(ground_reflections):
    """Utility function to calculate a factor that describes how much RF is increased by ground reflection.

    :param bool ground_reflections: Whether ground reflections are present
    :return: Coefficient (dimensionless) that other functions use to multiply EIRP
    :rtype: float
    :raises ValueError: if ground_reflections is not bool
    """
    if type(ground_reflections) != bool:
        raise ValueError("ground_reflections must be boolean: %s" % str(ground_reflections))
    if not ground_reflections:
        return 1
    else:
        return 1.6 * 1.6  # source: OET #65 pp. 20-21. EPA 520/6-85-011.


def effective_isotropic_radiated_power(antenna):
    """Calculate EIRP from feedpoint power, accounting for antenna gain and various time averaging of usage and mode.

    :param PoweredAntenna antenna:
    :return: Effective isotropic radiated power (milliwatts, NOTE change in units)
    :rtype: float
    :raises ValueError: if t_average or duty are not valid percentages (0 - 100 inclusive)
    """
    watts = antenna.watts
    duty = antenna.duty
    t_average = antenna.t_average
    dbi = antenna.dbi
    if not (0 <= t_average <= 100 and 0 <= duty <= 100):
        raise ValueError("t_average / duty out of range: %s / %s" % (str(t_average), str(duty)))
    milliwatts_average = 1000 * watts * (t_average / 100) * (duty / 100)
    return milliwatts_average * (10 ** (dbi / 10))


# Exemption functions #########


class RFEvaluationError(ValueError):
    pass


def is_exempt(watts, meters, mhz):
    """Determine via either MPE or SAR method whether a given power and frequency are exempt at a given distance.
    Not the same as RF evaluation.

    :param float watts: Power
    :param float meters: Distance from antenna to person (meters)
    :param float mhz: Frequency of the RF (megahertz)
    :return: A (bool, str) tuple stating whether this setup is exempt from evaluation, and the reason why / why not.
    :rtype: tuple
    """
    try:
        threshold, method = exempt_watts_generic(meters, mhz)
        return watts < threshold, method
    except RFEvaluationError:
        return False, 'nearfield'
    # Do not catch general ValueError, which means mhz may be out of range.


def exempt_watts_generic(meters, mhz):
    """Try both SAR and MPE exemption methods to find the best exemption threshold.

    :param float meters: Distance from antenna to person (meters)
    :param float mhz: Frequency of the RF (megahertz)
    :return: A (float, str) tuple stating the threshold (watts) and exemption method used
    :rtype: tuple
    """
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


def exempt_milliwatts_sar(cm, ghz):
    """Calculate power threshold for exemption from routine radio frequency exposure evaluation. Note: narrow range
    of applicable frequencies. FCC formula is "based on localized specific absorption rate (SAR) limits." Source: FCC
    19-126 p.23

    :param float cm: Distance from antenna to person (centimeters)
    :param float ghz: Frequency of RF source (gigahertz, NOTE different unit from other functions)
    :return: time-averaged power threshold for exemption (milliwatts)
    :rtype: float
    :raises ValueError: if frequency or distance out of range (0.3 - 6 GHz; 0 - 40 cm)
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
    """Calculate the effective radiated power threshold for exemption (exemption from RF exposure evaluation),
    using the maximum permissible exposure (MPE) method. Formulas based on FCC 19-126, Table 2, p. 26.

    :param float meters: Distance from source to area of interest (meters)
    :param float mhz: Frequency of the source (megahertz)
    :return: ERP threshold for exemption (watts)
    :rtype: float
    :raises RFEvaluationError: if distance is within "near field" (wavelength / (2*pi)), which triggers formal RF eval.
    :raises ValueError: if mhz is out of range (0.3 MHz - 100,000 MHz)
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
