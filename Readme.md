# Formulas for RF Exposure

Python implementation of the FCC's formulas for human exposure to
radiofrequency electromagnetic fields.


## Examples

    >>> import fcc
    >>> fcc.exempt_milliwatts_sar(1, 0.45)
    44.372516027834514

`exempt_milliwatts_sar(cm, ghz)` implements threshold power (P_th) for
SAR-based exemption (FCC 19-126, page 23). This example says that if
you have a 0.45 GHz (450 MHz) source, which is 1 cm away, you get a
SAR-based exemption if "each of the maximum time-averaged power or
maximum time-averaged ERP is no more than" **44.4 milliwatts.** This
method of exemption only applies to UHF or higher, not VHF or HF.

    >>> import fcc
    >>> fcc.exempt_watts_mpe(1, 444)
    5.6832

`fcc.exempt_watts_mpe(meters, mhz)` implements the MPE-based exemption
(FCC report p. 26) and returns an effective radiated power threshold
according to a formula. The example above means that a 444 MHz source
which is 1 meter away is exempt if its ERP is no more than **5.7
watts.** If the radiator is closer than a certain cutoff distance,
"evaluation is required" (p. 25, footnote 143). This method of
exemption works over a much broader range of frequencies.

Mind your units! They are all different magnitudes of units between
these two functions.

Run `python main.py` to do a test.


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

- Evaluation: ensuring "that the exposure limits are not exceeded in
  places that are accessible to people. In the great majority of
  cases, such an evaluation is simple and generic and does not require
  a determination of the precise exposure level..."

- mobile: normally 20cm or more from a person, e.g. desktop PC wifi

- portable: generally used *within* 20cm of the body
