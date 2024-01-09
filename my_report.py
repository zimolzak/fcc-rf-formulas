"""
Bottom line:
- controlled environment, stay 4 feet from any part of radiating structure.
- uncontrolled, stay 6 feet away.




The only variables I really care about are:
- frequency
- distance

Not so much:
- mode (assume CW, 40% duty and 100% time transmitting)
- power (assume 100 W)
- gain (assume 2.2)

Paul Evans, VP9KF recommends average power over:
- 30 minute time period for uncontrolled environments
- 6 minute time period for controlled environments (assume operating over the entire 6 min)

And he recommends these duty factors:
- Conversational SSB, no processing: 20%
- Conversational SSB, with processing: 40%
- [Voice] FM 100%
- FSK or RTTY 100%
- AFSK [SSB] 100%
- FT4/FT8 50%
- Conversational CW 40%
- Carrier 100%
 """
import fcc

freqs = [7.05, 14.05, 28.05, 50.05]
dipole_cw = fcc.PoweredAntenna(watts=100, t_average=100, duty=40, dbi=2.2)
for f in freqs:
    print(f, "MHz")
    print(fcc.RFEvaluationReport(dipole_cw, ft=6, mhz=f, ground_reflections=True))
    print()

"""
For controlled (6 min and 100% t average)
  (at 6 ft) Power density (mW/cm^2): 0.4043502039639964

7.05 MHz
MPE controlled (mW/cm^2): 18.107741059302853
Distance controlled (ft): 0.8965983719039542

14.05 MHz
MPE controlled (mW/cm^2): 4.559212775927356
Distance controlled (ft): 1.786837890106462

28.05 MHz
MPE controlled (mW/cm^2): 1.1438702851096685
Distance controlled (ft): 3.5673169265114772

50.05 MHz
MPE controlled (mW/cm^2): 1.0
Distance controlled (ft): 3.8153122208678902

Bottom line: members of household stay 3.815 feet (1.16 m) away from any part.
"""

print("\n\n========\n\nUNCONTROLLED\n\n")
dipole_cw_uncon = fcc.PoweredAntenna(watts=100, t_average=50, duty=40, dbi=2.2)
for f in freqs:
    print(f, "MHz")
    print(fcc.RFEvaluationReport(dipole_cw_uncon, ft=6, mhz=f, ground_reflections=True))
    print()

"""
For UNCONTROLLED (30 min and 50% t average)
  (at 6 ft) Power density (mW/cm^2): 0.2021751019819982

7.05 MHz
MPE uncontrolled (mW/cm^2): 3.62154821186057
Distance uncontrolled (ft): 1.4176465008076073

14.05 MHz
MPE uncontrolled (mW/cm^2): 0.9118425551854712
Distance uncontrolled (ft): 2.8252387711130336

28.05 MHz
MPE uncontrolled (mW/cm^2): 0.2287740570219337
Distance uncontrolled (ft): 5.640423311723884

50.05 MHz
MPE uncontrolled (mW/cm^2): 0.2
Distance uncontrolled (ft): 6.032538301308967

Everyone else, stay 6.0325 feet away (1.84 meters).
"""
