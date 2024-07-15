# Bottom line

- controlled environment, stay 4 feet from any part of radiating structure.
- uncontrolled, stay 6 feet away.


# Background

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

Per ARRL Handbook page 28.28:

> Although occupational/controlled limits are usually applicable in a
> workplace environment, the FCC has determined that they generally
> apply to amateur operators and members of their immediate
> households. In most cases, occupational/controlled limits can be
> applied to your home and property to which you can control physical
> access. The general population/uncontrolled limits are intend- ed
> for areas that are accessible by the general public, such as your
> neighbors’ properties

Furthermore...

Controlled:
: when they are aware of that exposure and can take steps to minimize it

Uncontrolled:
:  people who are not normally aware of the exposure or cannot exercise control over it. 




# Controlled results

```
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
```



# Uncontrolled results

```
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
```
