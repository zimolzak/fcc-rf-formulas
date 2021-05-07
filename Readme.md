# Formulas for RF Exposure

Python implementation of the FCC's formulas for human exposure to
radiofrequency electromagnetic fields. FCC rule changes go into effect on May
3, 2021.


## Examples

```python
import fcc
fcc.exempt_milliwatts_sar(1, 0.45)
# 44.372516027834514
```

This calculates threshold power (P_th) for SAR-based exemption (FCC
19-126, page 23). This example says that if you have a 0.45 GHz (450
MHz) source, which is 1 cm away, you get a SAR-based exemption if
"each of the maximum time-averaged power or maximum time-averaged ERP
is no more than" **44.4 milliwatts.** This method of exemption only
applies to UHF or higher, not VHF or HF.

```python
import fcc
fcc.exempt_watts_mpe(1, 444)
# 5.6832
```

This calculates effective radiated power threshold for MPE-based
exemption (FCC report p. 26). This example means that a 444 MHz source
which is 1 meter away is exempt if its ERP is no more than **5.7
watts.** If the radiator is closer than a certain cutoff distance,
"evaluation is required" (p. 25, footnote 143). This method of
exemption works over a much broader range of frequencies.

```python
fcc.exempt_watts_generic(0.01, 450)
# (0.04437251602783451, 'SAR')
fcc.exempt_watts_generic(1, 444)
# (5.6832, 'MPE')
fcc.exempt_watts_generic(0.16, 310)
# (0.5327389333009732, 'SAR wins')
```

This calculates a power threshold by the most favorable method
available.

```python
fcc.rf_evaluation_report(60, 50, 20, 2.2, 6, 29, True)
# {'Power density': 0.06065253059459946,
#  'MPE controlled': 1.070154577883472,
#  'MPE uncontrolled': 0.2140309155766944,
#  'Distance controlled': 1.428408600226954,
#  'Distance uncontrolled': 3.194018729752791,
#  'Compliant controlled': True,
#  'Compliant uncontrolled': True}
```

The function arguments mean (in order): 60 W at feedpoint, 50% usage, a mode with 20% duty (like SSB), 2.2 dBi gain
(like a dipole), distance of 6 feet from antenna, 29 MHz, and with ground reflection.

Mind your units! They may be different between some function arguments and
return values.


## Context

FCC released a report in 2019. The rule changes go into effect on May
3, 2021, hence the flurry of discussion of this topical matter.
Amateur (ham) radio is no longer categorically excluded from parts of
these rules. The report puts in place some "formula-based" exemptions.
They are not *too* complicated but have lots of piecewise function
definitions, "magic number" constants, etc. I have not seen any
computer code implementations so far.


## Links/references

https://docs.fcc.gov/public/attachments/FCC-19-126A1.pdf

http://www.arrl.org/news/updated-radio-frequency-exposure-rules-become-effective-on-may-3

Hare, Ed (W1RFI). *RF Exposure and You.* 1st ed., American Radio Relay
League, 1998-2003. This is a perfectly lovely book.
http://www.arrl.org/files/file/Technology/RFsafetyCommittee/RF+Exposure+and+You.pdf


## Abbreviations/definitions

- FCC: Federal Communications Commission (in the United States)

- SAR: specific absorption rate. Limits are specified in W/kg. Limits
  are set for whole-body, arbitrary tissue volumes, and certain body
  parts. Generally the less restrictive exemption.

- RF: radio frequency

- ERP: effective radiated power

- MPE: maximum permissible exposure. Limits are specified in V/m, A/m,
  and/or mW/cm^2. Limits sometimes derived from SAR limits. Different
  limits for controlled/uncontrolled areas.

- Exemption: when you *don't* have to do an RF exposure evaluation.
  There are 3 ways to be exempt (1 mW, SAR-based, and MPE-based).

- Evaluation: means ensuring "that the exposure limits are not
  exceeded in places that are accessible to people. In the great
  majority of cases, such an evaluation is simple and generic and does
  not require a determination of the precise exposure level..."
  (FCC p. 34). Per Ed Hare, "A routine evaluation is not nearly
  as onerous as it sounds!" "Most evaluations will not involve
  measurements," but will use charts, "straightforward calculations or
  computer modeling..." (Hare, p. 4.8).

- mobile: normally 20cm or more from a person, e.g. desktop PC wifi

- portable: generally used *within* 20cm of the body
