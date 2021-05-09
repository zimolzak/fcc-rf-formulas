import pytest
import fcc
import math
from fcc import CM_PER_FT, M_PER_FT, REPORT_KEYS


def test_is_compliant():
    # w t duty db ft mhz ground contr
    assert fcc.is_compliant(5, 50, 100, 2.2, 1, 420, False, True) == (True, 'evaluation')  # FM HT at 1 ft
    assert fcc.is_compliant(100, 50, 20, 2.2, 4, 29, False, False) == (True, 'evaluation')  # uncontrolled
    assert fcc.is_compliant(100, 50, 20, 2.2, 4, 29, False, True) == (True, 'evaluation')  # controlled
    # These 5 args don't matter if exempt
    t = 100
    du = 100
    db = 0
    gr = False
    co = False
    n = 0
    for ghz, cm, mw in fcc_table():
        # valid SAR thresholds
        w = mw / 1000
        ft = cm / CM_PER_FT
        mhz = ghz * 1000
        assert fcc.is_compliant(w * 0.9, t, du, db, ft, mhz, gr, co) == (True, 'SAR')
        # Shouldn't test w * 1.1, because some powers above MPE exemption will pass is_compliant() by eval.
        n += 1
    for meters, mhz in mpe_usable_values():
        # valid MPE thresholds
        w = fcc.exempt_watts_mpe(meters, mhz)
        ft = meters / M_PER_FT
        assert fcc.is_compliant(w * 0.9, t, du, db, ft, mhz, gr, co) == (True, 'MPE')
        n += 1
    print("\n    Looped %d tests of is_compliant()." % n, end='')


# Evaluation ########


def one_web(pwr, gain, meters, mhz, ground, expected, rel=0.05):
    report = fcc.rf_evaluation_report(pwr, 100, 100, gain, meters / M_PER_FT, mhz, ground)
    for i, k in enumerate(REPORT_KEYS):
        assert report[k] == pytest.approx(expected[i], rel=rel)  # percentage is surprisingly high


def test_rf_evaluation_report():
    one_web(123, 2, 10, 420, True, [0.0398, 1.41, 0.29, 5.58, 12.41, True, True])
    one_web(456, 3, 17, 123, True, [0.0642, 1.01, 0.21, 14.17, 31.63, True, True])
    one_web(111, 3.1, 11, 187, False, [0.015, 1.01, 0.21, 4.46, 9.9, True, True])
    one_web(1500, 2.2, 2, 146, False, [4.9525, 1.01, 0.21, 14.65, 32.7, False, False])
    one_web(200, 2.2, 2, 3.9, True, [1.6905, 59.18, 11.84, 1.16, 2.53, True, True])  # 80 m band
    one_web(1500, 2.2, 2, 3.9, True, [12.6784, 59.18, 11.84, 3.09, 6.84, True, False])  # 80 m, MOAR POWAR
    one_web(200, 2.2, 2, 10.110, True, [1.6905, 8.81, 1.77, 2.93, 6.48, True, True])  # 30 m
    one_web(5, 2.2, 0.1, 145.170, False, [6.6033, 1.01, 0.21, 0.89, 1.94, False, False], 0.06)  # HT on 2m


def test_mpe_limits_cont_uncont_mwcm2():
    with pytest.raises(ValueError):
        fcc.mpe_limits_cont_uncont_mwcm2(101000)  # mhz
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


def test_inverses():
    """distance = f(power, density)
    density = f(power, distance)
    """
    n = 0
    for feet in range(1, 300, 11):
        for milliwatts in range(100, 1000 * 100, 1131):
            density = fcc.power_density_mwcm2(milliwatts, feet, False)
            calc_feet = fcc.compliant_distance_ft(1, milliwatts, density)
            assert feet == pytest.approx(calc_feet)
            n += 1
    print("\n    Looped %d tests of inverses." % n, end='')


def test_power_density_mwcm2():
    # first principles
    cm = 100
    feet = cm / CM_PER_FT
    watts = 1000
    standard_density = watts / (4 * math.pi * (cm ** 2)) * 1000
    calculated_density = fcc.power_density_mwcm2(watts * 1000, feet, False)
    assert standard_density == pytest.approx(calculated_density)
    # web
    e = fcc.effective_isotropic_radiated_power(1, 100, 100, 2)
    assert fcc.power_density_mwcm2(e, 3 / M_PER_FT, True) == pytest.approx(0.0036, abs=1e-4)
    # throwaway
    fcc.power_density_mwcm2(1000, feet, True)
    # exceptions
    with pytest.raises(ValueError):
        fcc.power_density_mwcm2(1000, feet, 'durrr')
    with pytest.raises(ValueError):
        fcc.power_density_mwcm2(1000, feet, 'n')
    with pytest.raises(ValueError):
        fcc.power_density_mwcm2(1000, feet, 'y')
    with pytest.raises(ValueError):
        fcc.power_density_mwcm2(1000, feet, 42424242)


def test_effective_isotropic_radiated_power():
    n = 0
    for w in range(1, 20):
        assert w * 1000 == fcc.effective_isotropic_radiated_power(w, 100, 100, 0)  # isotropic
        n += 1
    for w in range(1, 20):
        assert w * 1000 * 10 == fcc.effective_isotropic_radiated_power(w, 100, 100, 10)  # 10 dB gain
        n += 1
    for w in range(1, 20):
        assert w * 1000 == fcc.effective_isotropic_radiated_power(w, 10, 10, 20)  # 20 dB, canceled by * 0.1 * 0.1
        n += 1
    print("\n    Looped %d tests of EIRP." % n, end='')
    with pytest.raises(TypeError):
        fcc.effective_isotropic_radiated_power(1000, 's', 100, 0)
    with pytest.raises(ValueError):
        fcc.effective_isotropic_radiated_power(1000, -3.1, 100, 0)
    with pytest.raises(ValueError):
        fcc.effective_isotropic_radiated_power(1000, 110, 50, 0)
    with pytest.raises(ValueError):
        fcc.effective_isotropic_radiated_power(1000, 100, 9999, 0)
    with pytest.raises(ValueError):
        fcc.effective_isotropic_radiated_power(1000, 100, -50, 0)
    with pytest.raises(ValueError):
        fcc.effective_isotropic_radiated_power(1000, -42, -50, 0)


# Exemption ########


def test_is_exempt():
    n = 0
    # watts, m, mhz are arguments to is_exempt()
    assert fcc.is_exempt(5, 1, 420) == (True, 'MPE')
    assert fcc.is_exempt(5, 0.1, 420)[0] is False
    with pytest.raises(ValueError):
        fcc.is_exempt(5, 0.1, 1234567890)
    for ghz, cm, mw in fcc_table():
        # valid SAR thresholds
        w = mw / 1000
        m = cm / 100
        mhz = ghz * 1000
        assert fcc.is_exempt(w * 0.9, m, mhz) == (True, 'SAR')
        assert fcc.is_exempt(w * 1.1, m, mhz)[0] is False
        n += 2
    for meters, mhz, why_exception in mpe_exception_values():
        # known NON-exemption
        if why_exception == 'freq':
            with pytest.raises(ValueError):
                fcc.is_exempt(0.42, meters, mhz)  # watts doesn't matter if freq invalid
        else:
            assert fcc.is_exempt(0.42, meters, mhz)[0] is False  # watts don't matter in near field
        n += 1
    for meters, mhz in mpe_usable_values():
        # valid MPE thresholds
        w = fcc.exempt_watts_mpe(meters, mhz)
        assert fcc.is_exempt(w * 0.9, meters, mhz) == (True, 'MPE')
        assert fcc.is_exempt(w * 1.1, meters, mhz)[0] is False
        n += 2
    print("\n    Looped %d tests of is_exempt()." % n, end='')


def test_exempt_watts_generic():
    n = 0
    for ghz, cm, mw in fcc_table():
        w, s = fcc.exempt_watts_generic(cm / 100, ghz * 1000)
        assert fcc_round(w * 1000) == mw
        n += 1
    for meters, mhz in mpe_usable_values():
        w, s = fcc.exempt_watts_generic(meters, mhz)  # throwaway
        n += 1
    pairs = [
        [41 / 100, 1 * 1000],  # fails SAR
        [20 / 100, 7 * 1000],  # fails SAR
        [99 / 100, 99 * 1000],  # fails SAR
        [0.398, 120],  # 120 mhz no SAR. 39.8 cm dist, 250 cm wavelength
        [0.16, 310]  # the rare overlap. 310 mhz, 97 cm /2pi = 15.4 cm
    ]
    for k, v in pairs:
        w, s = fcc.exempt_watts_generic(k, v)  # throwaway
        n += 1
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(20 / 100, 0.1 * 1000)
    with pytest.raises(ValueError):
        fcc.exempt_watts_generic(-1 / 100, 0.4 * 1000)
    for meters, mhz, dummy in mpe_exception_values():
        with pytest.raises(ValueError):
            fcc.exempt_watts_generic(meters, mhz)
        n += 1
    print("\n    Looped %d tests of exempt_watts_generic()." % n, end='')


def test_exempt_milliwatts_sar():
    n = 0
    for f, d, ref in fcc_table():
        result = fcc.exempt_milliwatts_sar(d, f)
        assert fcc_round(result) == ref
        n += 1
    print("\n    Looped %d tests of exempt_milliwatts_sar()." % n, end='')
    assert fcc_round(fcc.exempt_milliwatts_sar(40, 1.8)) == 3060
    # d     0   - 40
    # freq  0.3 -  6
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(41, 1)  # d high
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(20, 0.1)  # f low
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(20, 7)  # f high
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(99, 99)  # both high
    with pytest.raises(ValueError):
        fcc.exempt_milliwatts_sar(-1, 0.4)  # neg distance


def test_exempt_watts_mpe():
    """We are not (yet) asserting return vals. No external FCC ref
    available.
    """
    n = 0
    for meters, mhz in mpe_usable_values():
        fcc.exempt_watts_mpe(meters, mhz)  # throwaway
        n += 1
    for meters, mhz, dummy in mpe_exception_values():
        with pytest.raises(ValueError):
            fcc.exempt_watts_mpe(meters, mhz)
        n += 1
    print("\n    Looped %d tests of exempt_watts_mpe()." % n, end='')


# Utility functions/generators useful for testing


def mpe_exception_values():
    # all are R < L/2pi RFEvaluationError except as noted
    yield 0.01, 144, 'nearfield'
    yield 0.01, 239, 'nearfield'
    yield 3, 0.1, 'nearfield'
    yield 3, 1, 'nearfield'
    yield 4, 1, 'nearfield'
    yield 5, 1, 'nearfield'
    yield 6, 1, 'nearfield'
    yield 30000, 0.1, 'freq'  # freq 0.1 MHz too low
    yield 30000, 101000, 'freq'  # freq 101000 too high


def mpe_usable_values():
    # meters, mhz
    yield 1, 239
    yield 3, 20
    yield 3, 50
    yield 3, 100
    yield 3, 10000
    yield 50, 1
    yield 50, 100
    yield 50, 420
    yield 50, 2000
    yield 30000, 10000  # 17 GW LOL, buy SEVERAL power plants


def fcc_round(x):
    """Round as in FCC 19-126 Table 1, p. 23."""
    if x < 10:
        return round(x, 1)
    else:
        return int(round(x))


def test_fcc_round():
    assert fcc_round(39.1234) == 39
    assert fcc_round(22) == 22
    assert fcc_round(22.0) == 22
    assert fcc_round(2.1234) == 2.1
    assert fcc_round(9.0) == 9.0
    assert fcc_round(9.01234) == 9.0
    assert fcc_round(3060.1234) == 3060


def fcc_table():
    """Source: FCC 19-126, page 23, Table 1."""
    i = 0
    reference_mw = [39, 65, 88, 110, 22, 44, 67, 89, 9.2, 25, 44, 66]
    for ghz in [0.3, 0.45, 0.835]:  # First 3 rows of Table 1
        for cm in [0.5, 1, 1.5, 2]:  # First 4 columns
            yield ghz, cm, reference_mw[i]
            i += 1
