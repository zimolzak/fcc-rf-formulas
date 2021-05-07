import pytest
import fcc
import math


def test_stds():
    with pytest.raises(ValueError):
        fcc.mpe_limits_cont_uncont_mwcm2(101000)
    with pytest.raises(ValueError):
        fcc.mpe_limits_cont_uncont_mwcm2(0)
    with pytest.raises(ValueError):
        fcc.mpe_limits_cont_uncont_mwcm2(-12.34)
    # Non-exceptions, some assert, some throwaway
    assert fcc.mpe_limits_cont_uncont_mwcm2(1.2) == [100, 100]
    fcc.mpe_limits_cont_uncont_mwcm2(2)
    fcc.mpe_limits_cont_uncont_mwcm2(15)
    assert fcc.mpe_limits_cont_uncont_mwcm2(40) == [1, 0.2]
    assert fcc.mpe_limits_cont_uncont_mwcm2(3000) == [5, 1]


def test_density():
    cm = 100
    feet = cm / 30.48
    t = 1000 / (4 * math.pi * (cm ** 2)) * 1000
    L = fcc.power_density_antenna(1000, 100, 100, 0, feet, 420, False)
    assert L[0] == t
    fcc.power_density_antenna(1000, 100, 100, 0, feet, 420, True)
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 100, 100, 0, feet, 420, 'durrr')
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 100, 100, 0, feet, 420, 'n')
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 100, 100, 0, feet, 420, 'y')
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 100, 100, 0, feet, 420, 42424242)
    with pytest.raises(TypeError):
        fcc.power_density_antenna(1000, 's', 100, 0, feet, 420, False)
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, -3.1, 100, 0, feet, 420, False)
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 110, 50, 0, feet, 420, False)
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 100, 9999, 0, feet, 420, False)
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, 100, -50, 0, feet, 420, False)
    with pytest.raises(ValueError):
        fcc.power_density_antenna(1000, -42, -50, 0, feet, 420, False)


def test_generic():
    for ghz in [0.3, 0.45, 0.835]:
        for cm in [0.5, 1, 1.5, 2]:
            w, s = fcc.exempt_watts_generic(cm / 100, ghz * 1000)
            print(str(round(w, 3)) + " W, " + str(s))
    pairs = [
        [1, 239],
        [3, 20],
        [3, 50],
        [3, 100],
        [3, 10000],
        [50, 1],
        [50, 100],
        [50, 420],
        [50, 2000],
        [30000, 10000],
        [41/100, 1 * 1000],   # fails SAR
        [20/100, 7 * 1000],   # fails SAR
        [99/100, 99 * 1000],  # fails SAR
        [0.398, 120],  # 120 mhz no SAR. 39.8 cm dist, 250 cm wavelength
        [0.16, 310]  # the rare overlap. 310 mhz, 97 cm /2pi = 15.4 cm
    ]
    for k, v in pairs:
        w, s = fcc.exempt_watts_generic(k, v)
        print(str(round(w, 3)) + " W, " + str(s))


def test_generic_exceptions():
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(20/100, 0.1 * 1000)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(-1/100, 0.4 * 1000)
    # these are copy/pasted
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(0.01, 144)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(0.01, 239)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(3, 0.1)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(3, 1)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(4, 1)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(5, 1)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(6, 1)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(30000, 0.1)  # freq 0.1 MHz too low
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(30000, 101000)  # freq 101000 too high


def fcc_round(x):
    """Round as in FCC 19-126 Table 1, p. 23."""
    if x < 10:
        return (round(x, 1))
    else:
        return (int(round(x)))


def test_fcc_round():
    assert fcc_round(39.1234) == 39
    assert fcc_round(22) == 22
    assert fcc_round(22.0) == 22
    assert fcc_round(2.1234) == 2.1
    assert fcc_round(9.0) == 9.0
    assert fcc_round(9.01234) == 9.0
    assert fcc_round(3060.1234) == 3060


def test_all_sar():
    result_list = []
    reference = [39, 65, 88, 110, 22, 44, 67, 89, 9.2, 25, 44, 66]
    # reference is derived directly from FCC 19-126, Table 1.
    for f in [0.3, 0.45, 0.835]:  # First 3 rows of Table 1
        for d in [0.5, 1, 1.5, 2]:  # First 4 columns
            result = fcc.exempt_milliwatts_sar(d, f)
            printme = round(result, 1)
            compare = fcc_round(result)
            print(printme, end='\t')
            result_list.append(compare)
        print()
    print(result_list)
    assert result_list == reference
    assert fcc_round(fcc.exempt_milliwatts_sar(40, 1.8)) == 3060


def t_erpth(d, f):
    """This function is just used for printing"""
    erp = fcc.exempt_watts_mpe(d, f)
    print("%.0f m, %.0f MHz:\t%.1f W" % (d, f, erp))


def test_all_erp():
    """We are not (yet) asserting return vals. No external FCC ref
    available.
    """
    t_erpth(1, 239)
    t_erpth(3, 20)
    t_erpth(3, 50)
    t_erpth(3, 100)
    t_erpth(3, 10000)
    t_erpth(50, 1)
    t_erpth(50, 100)
    t_erpth(50, 420)
    t_erpth(50, 2000)
    t_erpth(30000, 10000)  # 17 GW LOL, buy SEVERAL power plants


def test_sar_exceptions():
    # d     0   - 40
    # freq  0.3 -  6
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(41, 1)    # d high
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(20, 0.1)  # f low
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(20, 7)    # f high
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(99, 99)   # both high
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(-1, 0.4)  # neg distance


def test_erp_exceptions():
    # all are R < L/2pi except as noted
    with pytest.raises(ValueError):
        t_erpth(0.01, 144)
    with pytest.raises(ValueError):
        t_erpth(0.01, 239)
    with pytest.raises(ValueError):
        t_erpth(3, 0.1)
    with pytest.raises(ValueError):
        t_erpth(3, 1)
    with pytest.raises(ValueError):
        t_erpth(4, 1)
    with pytest.raises(ValueError):
        t_erpth(5, 1)
    with pytest.raises(ValueError):
        t_erpth(6, 1)
    with pytest.raises(ValueError):
        t_erpth(30000, 0.1)  # freq 0.1 MHz too low
    with pytest.raises(ValueError):
        t_erpth(30000, 101000)  # freq 101000 too high
