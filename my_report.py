import fcc

freqs = [7.05, 14.05, 28.05, 50.05]
dipole_cw = fcc.PoweredAntenna(watts=100, t_average=100, duty=40, dbi=2.2)
for f in freqs:
    print(f, "MHz")
    print(fcc.RFEvaluationReport(dipole_cw, ft=6, mhz=f, ground_reflections=True))
    print()

print("\n\n========\n\nUNCONTROLLED\n\n")
dipole_cw_uncon = fcc.PoweredAntenna(watts=100, t_average=50, duty=40, dbi=2.2)
for f in freqs:
    print(f, "MHz")
    print(fcc.RFEvaluationReport(dipole_cw_uncon, ft=6, mhz=f, ground_reflections=True))
    print()
