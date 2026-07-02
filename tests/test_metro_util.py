import unittest

import numpy

import tests  # noqa: F401  (sets up sys.path, see tests/__init__.py)

from toolbox import metro_util
import metro_error


class TestJoinDictionaries(unittest.TestCase):

    def test_second_dict_wins_on_key_conflict(self):
        result = metro_util.join_dictionaries({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
        self.assertEqual(result, {'a': 1, 'b': 3, 'c': 4})

    def test_originals_are_not_mutated(self):
        d1 = {'a': 1}
        d2 = {'b': 2}
        metro_util.join_dictionaries(d1, d2)
        self.assertEqual(d1, {'a': 1})
        self.assertEqual(d2, {'b': 2})


class TestList2String(unittest.TestCase):

    def test_empty_list(self):
        self.assertEqual(metro_util.list2string([]), "")

    def test_single_element(self):
        self.assertEqual(metro_util.list2string([1]), "1")

    def test_multiple_elements_are_comma_separated(self):
        self.assertEqual(metro_util.list2string(["a", "b", 3]), "a, b, 3")


class TestIsArrayUniform(unittest.TestCase):

    def test_uniform_array_is_true(self):
        self.assertTrue(metro_util.is_array_uniform(numpy.array([0.0, 10.0, 20.0, 30.0])))

    def test_non_uniform_array_is_false(self):
        self.assertFalse(metro_util.is_array_uniform(numpy.array([0.0, 5.0, 20.0, 30.0])))


class TestInterpolate(unittest.TestCase):

    def test_linear_ramp_interpolates_between_known_points(self):
        xArray = numpy.array([0.0, 3600.0, 7200.0])
        yArray = numpy.array([0.0, 10.0, 20.0])
        result = metro_util.interpolate(xArray, yArray)
        # numpy.arange's stop bound is exclusive, so the ramp approaches but
        # never quite reaches the last x value.
        self.assertAlmostEqual(result[0], 0.0, places=3)
        self.assertGreater(result[-1], 19.0)
        self.assertLess(result[-1], 20.0)
        self.assertTrue((numpy.diff(result) >= 0).all())


class TestValidateVersionNumber(unittest.TestCase):

    def test_version_within_range_is_accepted(self):
        metro_util.validate_version_number("1.5", "1.0", "1.6")

    def test_version_too_old_raises(self):
        with self.assertRaises(metro_error.Metro_version_error):
            metro_util.validate_version_number("0.9", "1.0", "1.6")

    def test_version_too_new_raises(self):
        with self.assertRaises(metro_error.Metro_version_error):
            metro_util.validate_version_number("2.0", "1.0", "1.6")

    def test_missing_version_raises(self):
        with self.assertRaises(metro_error.Metro_version_error):
            metro_util.validate_version_number(None, "1.0", "1.6")


class TestInitTranslationFallback(unittest.TestCase):

    def test_unknown_domain_falls_back_instead_of_raising(self):
        # A module name with no compiled .mo must not crash METRo (see the
        # fallback=True fix in metro_util.init_translation).
        translate = metro_util.init_translation("this_module_does_not_exist")
        self.assertEqual(translate("hello"), "hello")


if __name__ == '__main__':
    unittest.main()
