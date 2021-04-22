from math import log10, sqrt

def pth(d,f):
    """d in cm, f in GHz. Source: FCC 19-126 p.23"""
    if 0.3 <= f < 1.5:
        erp20 = 2040 * f
    elif 1.5 <= f <= 6:
        erp20 = 3060
    else:
        raise Exception('frequency out of range: ' + str(f))
    x = -1 * log10(60 / (erp20 * sqrt(f)))
    if d <= 20:
        P_threshold = erp20 * (d / 20) ** x
    elif 20 < d <= 40:
        P_threshold = erp20
    else:
        raise Exception('distance out of range: ' + str(d))
    return(P_threshold)
