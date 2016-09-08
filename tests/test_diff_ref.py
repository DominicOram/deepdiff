#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run only the search tests:
    python -m unittest tests.diff_tests

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    python -m unittest tests.DeepDiffTestCase.test_list_of_sets_difference_ignore_order
"""
import unittest
import datetime
from decimal import Decimal
from deepdiff import DeepDiff
import logging

from deepdiff.helper import py3
from deepdiff.model import DictRelationship

from tests import CustomClass


logging.disable(logging.CRITICAL)


class DeepDiffRefTestCase(unittest.TestCase):

    """DeepDiff Tests."""

    def test_same_objects(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = t1
        ddiff = DeepDiff(t1, t2)
        res = ddiff.result_refs
        self.assertEqual(res, {})

    def test_item_added_extensive(self):
        t1 = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
        t2 = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'new': 1337}
        ddiff = DeepDiff(t1, t2)
        res = ddiff.result_refs
        self.assertEqual(set(res.keys()), {'dictionary_item_added'})
        self.assertEqual(len(res['dictionary_item_added']), 1)

        (added1,) = res['dictionary_item_added']

        # assert added1 DiffLevel chain is valid at all
        self.assertEqual(added1.up.down, added1)
        self.assertIsNone(added1.down)
        self.assertIsNone(added1.up.up)
        self.assertEqual(added1.all_up(), added1.up)
        self.assertEqual(added1.up.all_down(), added1)
        self.assertEqual(added1.report_type, 'dictionary_item_added')

        # assert DiffLevel chain points to the objects we entered
        self.assertEqual(added1.up.t1, t1)
        self.assertEqual(added1.up.t2, t2)

        self.assertEqual(added1.t1, None)
        self.assertEqual(added1.t2, 1337)

        # assert DiffLevel child relationships are correct
        self.assertIsNone(added1.up.t1_child_rel)
        self.assertIsInstance(added1.up.t2_child_rel, DictRelationship)
        self.assertEqual(added1.up.t2_child_rel.parent, added1.up.t2)
        self.assertEqual(added1.up.t2_child_rel.child, added1.t2)
        self.assertEqual(added1.up.t2_child_rel.param, 'new')

        self.assertEqual(added1.up.path(), "root")
        self.assertEqual(added1.path(), "root['new']")

    def test_item_added_and_removed(self):
        t1 = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
        t2 = {'one': 1, 'two': 4, 'three': 3, 'five': 5, 'six': 6}
        ddiff = DeepDiff(t1, t2, default_view='ref')
        res = ddiff
        self.assertEqual(set(res.keys()),
                         {'dictionary_item_added', 'dictionary_item_removed', 'values_changed'})
        self.assertEqual(len(res['dictionary_item_added']), 2)
        self.assertEqual(len(res['dictionary_item_removed']), 1)
