from math import log10, sqrt, pi

def pth(d,f):
    """Calculate time-averaged power threshold for exemption, for radio
    frequency sources. (Exemption from routine RF exposure
    evaluation.) Note, this is only for UHF and part of SHF. Not
    applicable to VHF, HF, and frequencies below. FCC formula is
    'based on localized specific absorption rate (SAR) limits.' For
    lower frequencies, you need to look at MPE-based exemption with
    ERP threshold, not SAR-based.

    d in cm, f in GHz. Return value in mW. Source: FCC 19-126 p.23

    """
    if 0.3 <= f < 1.5:
        erp20 = 2040 * f
    elif 1.5 <= f <= 6:
        erp20 = 3060
    else:
        raise Exception('frequency out of range: ' + str(f) + ' GHz')
    x = -1 * log10(60 / (erp20 * sqrt(f)))
    if d <= 20:
        P_threshold = erp20 * (d / 20) ** x
    elif 20 < d <= 40:
        P_threshold = erp20
    else:
        raise Exception('distance out of range: ' + str(d) + ' cm')
    return(P_threshold)

CUTPOINTS = [0.3, 1.34, 30, 300, 1500, 100000]

def f1(f,r): return(1920 * r**2)
def f2(f,r): return(33450 * r**2 / f**2)
def f3(f,r): return(3.83 * r**2)
def f4(f,r): return(0.0128 * r**2 * f)
def f5(f,r): return(19.2 * r**2)
FUNCTIONS = [f1, f2, f3, f4, f5]

def erpth(d,f):
    """ d in meters, f in MHz, return val in watts. """
    c = 299792458    # m/s
    nu = f * 1E6     # Hz
    lambd = c / nu  # m
    L2p = lambd / (2 * pi)
    if d < L2p:
        print('R=' + str(d) + ', L/(2pi) = ' + str(round(L2p, 2)) + 'm')
        raise Exception('R < L/(2pi), therefore RF evaluation required.')
    for i in range(len(CUTPOINTS)):
        if i == len(CUTPOINTS) - 1:
            raise Exception("f = " + str(f) + ' MHz is not in my table.')
        f_low = CUTPOINTS[i]
        f_high = CUTPOINTS[i + 1]
        if f_low <= f < f_high:
            return(FUNCTIONS[i](f, d))
    raise Exception('Reached end; freq not in table: ' + str(f) + ' MHz')
