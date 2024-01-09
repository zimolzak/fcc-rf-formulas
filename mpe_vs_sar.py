import math
import fcc

for n in range(3, 60):
    ghz = n / 10
    for cm in range(1, 41):
        try:
            wm = fcc.exempt_watts_mpe(cm / 100, ghz * 1000)
        except fcc.RFEvaluationError:
            continue
        ws = fcc.exempt_milliwatts_sar(cm, ghz) / 1000
        if wm > ws:
            print("%f ghz %f cm %f W MPE %f W SAR" % (ghz, cm, wm, ws))

print()

for mhz10 in range(0, 10000, 100):
    mhz = mhz10 / 10 + 0.3
    for meters in range(1, 100):
        try:
            w_exempt = fcc.exempt_watts_mpe(meters, mhz)
        except fcc.RFEvaluationError:
            w_exempt = 0
        dens_c, dens_u = fcc.mpe_limits_cont_uncont_mwcm2(mhz)
        cm = meters * 100
        # denisty = eirp_mw / (4 * math.pi * (cm ** 2)). Therefore...
        eirp_w_c = dens_c * (4 * math.pi * (cm ** 2)) / 1000
        eirp_w_u = dens_u * (4 * math.pi * (cm ** 2)) / 1000
        if 0 < w_exempt < 200:
            ratio1 = eirp_w_u / w_exempt
            ratio2 = eirp_w_c / eirp_w_u
            print("{} mhz, {} m, {} W exempt, {} W uncont, {} W cont\t{} {}".format(mhz, meters,
                                                                                    round(w_exempt, 1),
                                                                                    round(eirp_w_u, 1),
                                                                                    round(eirp_w_c, 1),
                                                                                    ratio1,
                                                                                    round(ratio2, 4),
                                                                                    ))
# ratio 1 is maybe near 25 * pi / 12 ??
