"""Test bin_columns, manual cutoffs"""
import unittest
import pandas as pd
import numpy as np

from sparktkregtests.lib import sparktk_test



class BinColTest(sparktk_test.SparkTKTestCase):

    # baseline cutoffs
    cutoff_list = [0, 10, 100, 400, 800, 1000]

    def setUp(self):
        """Build test frames"""
        super(BinColTest, self).setUp()

        dataset = self.get_file("count_letters.csv")
        schema = [("index", int), ("letter", str)]

        self.frame = self.context.frame.import_csv(dataset, schema=schema)

    def test_bin_column_name_collision(self):
        """Validate default naming convention"""
        # Call bin_col multiple times to force collisions with column names.
        self.frame.bin_column("index", 10)
        self.frame.bin_column("index", 10)
        self.frame.bin_column("index", 10)
        self.frame.bin_column("index", 10)
        self.frame.bin_column("index", 10)
        self.frame.bin_column("index", 10)

        self.assertIn("index_binned_0", self.frame.column_names)
        self.assertIn("index_binned_1", self.frame.column_names)
        self.assertIn("index_binned_2", self.frame.column_names)
        self.assertIn("index_binned_3", self.frame.column_names)
        self.assertIn("index_binned_4", self.frame.column_names)

        self.frame.drop_columns("index_binned_0")
        self.assertNotIn("index_binned_0", self.frame.column_names)
        self.frame.bin_column("index", 10)
        self.assertIn("index_binned_0", self.frame.column_names)

    def test_bin_column_cutoff_multi(self):
        """Test multiple coutoffs"""
        self.frame.bin_column("index", self.cutoff_list)
        frame_take = self.frame.take(self.frame.count()).data

        for i in frame_take:
            if i[0] < 10:
                self.assertEqual(i[2], 0)
            elif i[0] < 100:
                self.assertEqual(i[2], 1)
            elif i[0] < 400:
                self.assertEqual(i[2], 2)
            elif i[0] < 800:
                self.assertEqual(i[2], 3)
            else:
                self.assertEqual(i[2], 4)

    @unittest.skip("tupled cutoffs not accepted")
    def test_bin_column_tuple_params(self):
        """Validate mutliple cutoffs with tupled parameters"""
        cutoff_tuple = tuple(self.cutoff_list)
        self.frame.bin_column("index", cutoff_tuple)
        frame_take = self.frame.take(self.frame.count()).data

        for i in frame_take:
            if i[0] < 10:
                self.assertEqual(i[2], 0)
            elif i[0] < 100:
                self.assertEqual(i[2], 1)
            elif i[0] < 400:
                self.assertEqual(i[2], 2)
            elif i[0] < 800:
                self.assertEqual(i[2], 3)
            else:
                self.assertEqual(i[2], 4)

    def test_bin_column_one_bin(self):
        """Test binning on one column, non strict binning without lowest"""
        cutoff_diad = [0, 1000]

        self.frame.bin_column("index",
                              cutoff_diad,
                              include_lowest=False,
                              strict_binning=True,
                              bin_column_name="single_bin")

        frame_take = self.frame.take(self.frame.count()).data

        for i in frame_take:
            self.assertEqual(i[2], 0)

    def test_bin_column_cutoff_monad(self):
        """Test no legal bin"""
        cutoff_monad = [-131]
        with self.assertRaisesRegexp(Exception, "number of bins"):
            self.frame.bin_column("index", cutoff_monad)

    def test_bin_column_bad_col(self):
        """Test bad column name"""
        with self.assertRaisesRegexp(Exception, "Invalid column name"):
            self.frame.bin_column(
                "non_existent_name",
                self.cutoff_list, bin_column_name="letters")

    def test_bin_column_cutoff_string(self):
        """Test bad cutoff type, string"""
        with self.assertRaisesRegexp(ValueError, "convert string"):
            self.frame.bin_column(
                "index", "su", bin_column_name="tr_te_va_bin")

    def test_bin_column_cutoff_string_list(self):
        """Test bad cutoff type, list of strings"""
        with self.assertRaisesRegexp(ValueError, "convert string"):
            self.frame.bin_column("index", ["a", "b"])

    def test_bin_column_cutoff_none(self):
        """None for bin cutoffs errors"""
        with self.assertRaisesRegexp(TypeError, "must be a string"):
            self.frame.bin_column("index", None)

    @unittest.skip("empty list of cutoffs is accepted")
    def test_bin_column_cutoff_empty(self):
        """Test reject empty cutoff list"""
        with self.assertRaises(Exception):
            self.frame.bin_column("index", [])

    @unittest.skip("descending cutoffs are allowed")
    def test_bin_column_cutoff_mixed(self):
        """Test error cutoffs are not monotonic """
        with self.assertRaises(Exception):
            self.frame.bin_column(
                "index", self.cutoff_list+[-5511], bin_column_name="no_bin")

    @unittest.skip("descending cutoffs are allowed")
    def test_bin_column_cutoff_desc(self):
        """ API doc allows monotonic in either direction """
        cutoff_desc = self.cutoff_list[::-1]

        with self.assertRaises(Exception):
            self.frame.bin_column("index", cutoff_desc)
            self.frame.inspect()

    def test_bin_column_name_dup(self):
        """ Duplicate column errors"""
        with self.assertRaisesRegexp(Exception, "duplicated"):
            self.frame.bin_column(
                "index", self.cutoff_list, bin_column_name='index')


if __name__ == "__main__":
    unittest.main()
