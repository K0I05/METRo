import unittest

import tests  # noqa: F401  (sets up sys.path, see tests/__init__.py)

from toolbox import metro_grip


class TestComputeGrip(unittest.TestCase):

    def test_dry_road_is_fixed_at_grip_dry(self):
        grip = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_DRY, 0.0, 0.0, -5.0, 0.0)
        self.assertEqual(grip, metro_grip.GRIP_DRY)

    def test_dew_is_fixed_at_grip_dew(self):
        grip = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_DEW, 0.0, 0.0, 2.0, 0.0)
        self.assertEqual(grip, metro_grip.GRIP_DEW)

    def test_wet_road_grip_decreases_as_water_depth_increases(self):
        thin = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_WET, 0.3, 0.0, 5.0, 0.0)
        thick = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_WET, 8.0, 0.0, 5.0, 0.0)
        self.assertGreater(thin, thick)
        self.assertAlmostEqual(thick, metro_grip.GRIP_WET_MIN, places=2)

    def test_wet_road_grip_is_clamped_beyond_saturation_depth(self):
        at_saturation = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_WET,
                                                 metro_grip.WATER_FILM_SATURATION_MM, 0.0, 5.0, 0.0)
        way_beyond = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_WET,
                                             metro_grip.WATER_FILM_SATURATION_MM * 10, 0.0, 5.0, 0.0)
        self.assertEqual(at_saturation, way_beyond)

    def test_ice_grip_is_worse_near_freezing_point_than_when_colder(self):
        near_freezing = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_ICE_SNOW, 0.0, 0.3, -0.5, 0.0)
        much_colder = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_ICE_SNOW, 0.0, 0.3, -20.0, 0.0)
        self.assertLess(near_freezing, much_colder)

    def test_frost_saturates_at_a_much_thinner_depth_than_ice_snow(self):
        thin_ice_mm = 0.3
        thin_ice_cm = thin_ice_mm / 10.0
        frost = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_FROST, 0.0, thin_ice_cm, -1.0, 0.0)
        ice_snow = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_ICE_SNOW, 0.0, thin_ice_cm, -1.0, 0.0)
        self.assertLess(frost, ice_snow)

    def test_salted_road_stays_wetter_and_grippier_than_untreated_ice_at_same_temp(self):
        # At -2 C an untreated road (freezing point 0 C) has already frozen,
        # so METRo reports RC=ICE_SNOW there; a salted road (freezing point
        # -5 C) is still simply wet at that same temperature (RC=WET), since
        # its effective freezing point has not been reached yet. This is
        # where the "grip stays higher for longer on a salted road" effect
        # actually shows up: in which RC state the road is in, not in
        # comparing two ICE_SNOW readings at mismatched freezing points.
        untreated_ice = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_ICE_SNOW, 0.0, 0.1, -2.0, 0.0)
        salted_wet = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_WET, 1.0, 0.0, -2.0, -5.0)
        self.assertGreater(salted_wet, untreated_ice)

    def test_icing_rain_stays_low_even_when_very_cold(self):
        grip = metro_grip.compute_grip(metro_grip.ROAD_CONDITION_ICING_RAIN, 0.0, 0.0, -30.0, 0.0)
        self.assertLessEqual(grip, metro_grip.GRIP_ICING_RAIN_MAX_COLD)

    def test_grip_is_always_within_zero_one_across_a_value_sweep(self):
        surface_temps = [-30.0, -15.0, -5.0, -1.0, 0.0, 1.0, 5.0]
        depths = [0.0, 0.1, 0.5, 1.0, 3.0, 10.0]
        for rc in range(1, 9):
            for temp in surface_temps:
                for depth in depths:
                    grip = metro_grip.compute_grip(rc, depth, depth, temp, 0.0)
                    self.assertGreaterEqual(grip, 0.0, msg="rc=%d temp=%s depth=%s" % (rc, temp, depth))
                    self.assertLessEqual(grip, 1.0, msg="rc=%d temp=%s depth=%s" % (rc, temp, depth))

    def test_unknown_road_condition_falls_back_to_dry(self):
        self.assertEqual(metro_grip.compute_grip(99, 0.0, 0.0, -5.0, 0.0), metro_grip.GRIP_DRY)


if __name__ == '__main__':
    unittest.main()
