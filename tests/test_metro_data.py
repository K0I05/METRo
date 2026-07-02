import math
import unittest

import tests  # noqa: F401  (sets up sys.path, see tests/__init__.py)

from data_module.metro_data import Metro_data
import metro_error


STD_ITEMS = [{'NAME': "AT"}, {'NAME': "TD"}]
EXT_ITEMS = [{'NAME': "FA"}]


class TestMetroDataColumns(unittest.TestCase):

    def test_column_names_are_standard_plus_extended(self):
        data = Metro_data(STD_ITEMS, EXT_ITEMS)
        self.assertEqual(data.get_matrix_col_list(), ["AT", "TD", "FA"])
        self.assertTrue(data.is_standardCol("AT"))
        self.assertFalse(data.is_standardCol("FA"))

    def test_append_and_get_matrix_row(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, 2.0])
        data.append_matrix_row([3.0, 4.0])
        self.assertEqual(data.get_matrix_col("AT").tolist(), [1.0, 3.0])
        self.assertEqual(data.get_matrix_col("TD").tolist(), [2.0, 4.0])

    def test_append_matrix_row_replaces_none_with_nan(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, None])
        self.assertTrue(math.isnan(data.get_matrix_col("TD")[0]))
        self.assertEqual(data.get_matrix_col("AT")[0], 1.0)

    def test_del_matrix_row_removes_correct_rows(self):
        data = Metro_data(STD_ITEMS)
        for i in range(5):
            data.append_matrix_row([float(i), float(i) * 10])
        data.del_matrix_row([1, 3])
        self.assertEqual(data.get_matrix_col("AT").tolist(), [0.0, 2.0, 4.0])

    def test_set_matrix_col_overwrites_existing_column(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, 2.0])
        data.append_matrix_row([3.0, 4.0])
        data.set_matrix_col("TD", [20.0, 40.0])
        self.assertEqual(data.get_matrix_col("TD").tolist(), [20.0, 40.0])

    def test_set_matrix_col_rejects_unknown_column(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, 2.0])
        with self.assertRaises(metro_error.Metro_data_error):
            data.set_matrix_col("NOT_A_COLUMN", [1.0])

    def test_append_matrix_col_adds_new_extended_column(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, 2.0])
        data.append_matrix_row([3.0, 4.0])
        data.append_matrix_col("GRIP", [0.9, 0.5])
        self.assertEqual(data.get_matrix_col("GRIP").tolist(), [0.9, 0.5])
        self.assertIn("GRIP", data.lMatrix_ext_col_name)

    def test_append_matrix_col_rejects_duplicate_name(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, 2.0])
        data.append_matrix_col("GRIP", [0.9])
        with self.assertRaises(metro_error.Metro_data_error):
            data.append_matrix_col("GRIP", [0.1])

    def test_readonly_blocks_mutation(self):
        data = Metro_data(STD_ITEMS)
        data.append_matrix_row([1.0, 2.0])
        data.set_readonly(True)
        self.assertTrue(data.is_readonly())
        with self.assertRaises(metro_error.Metro_data_error):
            data.append_matrix_row([3.0, 4.0])

    def test_header_get_set(self):
        data = Metro_data(STD_ITEMS)
        data.set_header({'VERSION': "1.6"})
        self.assertEqual(data.get_header_value("VERSION"), "1.6")
        with self.assertRaises(metro_error.Metro_data_error):
            data.get_header_value("NOT_A_KEY")


if __name__ == '__main__':
    unittest.main()
