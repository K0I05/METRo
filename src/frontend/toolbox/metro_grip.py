# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006
#
#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
###################################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


"""
    Name: metro_grip

    Description: Derives a road grip / traction index (0.0 = essentially no
                 traction, 1.0 = dry bare pavement) from quantities METRo
                 already computes: road condition code (RC), liquid water
                 depth (RA, mm), snow/ice water-equivalent depth (SN, cm),
                 surface temperature (ST, C) and the effective freezing
                 point of water (C, 0.0 unless --use-freezing-point-forecast
                 is used).

                 This is a heuristic, not a physical measurement: no fixed
                 sensor (nor METRo) can observe tire-pavement contact
                 mechanics. Commercial pavement sensors such as the Lufft
                 IRS31/NIRS31 derive a friction/grip value the same way,
                 from lookup tables and empirical thresholds over surface
                 state, water film depth and ice percentage - this module
                 follows the same approach:
                   - dry/damp pavement stays near maximum grip;
                   - grip degrades smoothly as water film depth increases
                     (aquaplaning risk);
                   - grip degrades rapidly as ice/snow depth increases;
                   - ice friction is not monotonic with temperature: it is
                     worst near the freezing point (thin lubricating
                     meltwater film) and partially recovers at colder
                     temperatures (harder, drier ice);
                   - using the effective freezing point (rather than a
                     hardcoded 0 C) means a salted/treated road (lower
                     freezing point) keeps a higher grip value for longer
                     below 0 C, the same "saline compensation" effect
                     described for the Lufft sensors.

                 The constants below are not calibrated against any real
                 sensor or field data; they encode the qualitative shape of
                 the relationships above at a plausible scale. Treat this as
                 a starting point for winter-maintenance decision support,
                 not a validated friction measurement.
"""

# Grip value for dry pavement (RC=1) and the ceiling every other state is
# scaled down from.
GRIP_DRY = 0.95

# Dew (RC=5): thin condensation film, small penalty vs fully dry.
GRIP_DEW = 0.85

# Wet road (RC=2): grip decreases as the water film (RA, mm) thickens,
# saturating at a level associated with meaningful hydroplaning risk.
GRIP_WET_MAX = 0.85
GRIP_WET_MIN = 0.45
WATER_FILM_SATURATION_MM = 5.0

# Melting snow (RC=6): wet slush, lower ceiling than plain wet road.
GRIP_MELTSNOW_MAX = 0.55
GRIP_MELTSNOW_MIN = 0.25
SNOW_DEPTH_SATURATION_CM = 1.0

# Ice/snow on the road (RC=3) and frost/black ice (RC=7): grip collapses as
# ice depth increases, then partially recovers as it gets colder (see
# _ice_grip below). Frost/black ice saturates at a much smaller depth since,
# unlike bulk snow/ice accumulation, even a barely-measurable film is
# already dangerous.
GRIP_ICE_MIN = 0.05
GRIP_ICE_MAX_COLD = 0.35
ICE_DEPTH_SATURATION_MM = 2.0
FROST_DEPTH_SATURATION_MM = 0.05
ICE_COLD_RECOVERY_DEGREES = 15.0

# Mix water/snow (RC=4): take the worse of the wet and icy components.
GRIP_MIX_MIN = 0.15
GRIP_MIX_MAX = 0.35

# Icing rain / glaze (RC=8): a famously dangerous, thin and uniform ice
# layer that forms immediately on contact. Depth is not a meaningful factor
# here (unlike RC=3/7); only the cold-recovery effect is applied.
GRIP_ICING_RAIN_MIN = 0.03
GRIP_ICING_RAIN_MAX_COLD = 0.15

ROAD_CONDITION_DRY = 1
ROAD_CONDITION_WET = 2
ROAD_CONDITION_ICE_SNOW = 3
ROAD_CONDITION_MIX_WATER_SNOW = 4
ROAD_CONDITION_DEW = 5
ROAD_CONDITION_MELTING_SNOW = 6
ROAD_CONDITION_FROST = 7
ROAD_CONDITION_ICING_RAIN = 8


def _clamp01(fValue):
    return max(0.0, min(1.0, fValue))


def _lerp_clamped(fValue, fX0, fX1, fY0, fY1):
    """ Linearly interpolate fValue from range [fX0, fX1] to [fY0, fY1], clamped to that range. """
    if fX1 == fX0:
        return fY0
    fT = _clamp01((fValue - fX0) / (fX1 - fX0))
    return fY0 + fT * (fY1 - fY0)


def _ice_grip(fDepthMM, fDepthSaturationMM, fSurfaceTempC, fFreezingPointC, fGripMin, fGripMaxCold):
    """
        Grip for an icy surface: degrades as ice depth approaches
        fDepthSaturationMM, then partially recovers with colder temperatures
        (relative to the effective freezing point).
    """
    fDegreesBelowFreezing = max(0.0, fFreezingPointC - fSurfaceTempC)
    fTempFactor = _clamp01(fDegreesBelowFreezing / ICE_COLD_RECOVERY_DEGREES)
    fDepthFactor = _clamp01(fDepthMM / fDepthSaturationMM) if fDepthSaturationMM > 0 else 1.0
    fGripAtSaturation = fGripMin + fTempFactor * (fGripMaxCold - fGripMin)
    return GRIP_DRY - fDepthFactor * (GRIP_DRY - fGripAtSaturation)


def compute_grip(nRoad_condition, fWaterDepthMM, fSnowDepthCM, fSurfaceTempC, fFreezingPointC=0.0):
    """
        Name: compute_grip

        Parameters: [I] nRoad_condition : METRo road condition code (RC), 1-8
                    [I] fWaterDepthMM : liquid water depth on the road (RA), mm
                    [I] fSnowDepthCM : snow/ice water-equivalent depth on the road (SN), cm
                    [I] fSurfaceTempC : road surface temperature, Celsius
                    [I] fFreezingPointC : effective freezing point of water, Celsius (0.0 for pure water)

        Returns: grip index, float in [0.0, 1.0]
    """
    fSnowDepthMM = fSnowDepthCM * 10.0

    if nRoad_condition == ROAD_CONDITION_DRY:
        return GRIP_DRY

    if nRoad_condition == ROAD_CONDITION_WET:
        return _lerp_clamped(fWaterDepthMM, 0.2, WATER_FILM_SATURATION_MM, GRIP_WET_MAX, GRIP_WET_MIN)

    if nRoad_condition == ROAD_CONDITION_ICE_SNOW:
        return _ice_grip(fSnowDepthMM, ICE_DEPTH_SATURATION_MM, fSurfaceTempC, fFreezingPointC,
                          GRIP_ICE_MIN, GRIP_ICE_MAX_COLD)

    if nRoad_condition == ROAD_CONDITION_MIX_WATER_SNOW:
        fWet_component = _lerp_clamped(fWaterDepthMM, 0.2, WATER_FILM_SATURATION_MM, GRIP_WET_MAX, GRIP_WET_MIN)
        fIce_component = _ice_grip(fSnowDepthMM, ICE_DEPTH_SATURATION_MM, fSurfaceTempC, fFreezingPointC,
                                    GRIP_MIX_MIN, GRIP_MIX_MAX)
        return min(fWet_component, fIce_component)

    if nRoad_condition == ROAD_CONDITION_DEW:
        return GRIP_DEW

    if nRoad_condition == ROAD_CONDITION_MELTING_SNOW:
        return _lerp_clamped(fSnowDepthCM, 0.0, SNOW_DEPTH_SATURATION_CM, GRIP_MELTSNOW_MAX, GRIP_MELTSNOW_MIN)

    if nRoad_condition == ROAD_CONDITION_FROST:
        return _ice_grip(fSnowDepthMM, FROST_DEPTH_SATURATION_MM, fSurfaceTempC, fFreezingPointC,
                          GRIP_ICE_MIN, GRIP_ICE_MAX_COLD)

    if nRoad_condition == ROAD_CONDITION_ICING_RAIN:
        fDegreesBelowFreezing = max(0.0, fFreezingPointC - fSurfaceTempC)
        fTempFactor = _clamp01(fDegreesBelowFreezing / ICE_COLD_RECOVERY_DEGREES)
        return GRIP_ICING_RAIN_MIN + fTempFactor * (GRIP_ICING_RAIN_MAX_COLD - GRIP_ICING_RAIN_MIN)

    # Unknown/unexpected RC code: fall back to the safest assumption.
    return GRIP_DRY
