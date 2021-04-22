from math import log10, sqrt

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
