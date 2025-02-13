# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.


import json
import os
import unittest

from pymatgen.core.composition import Composition
from pymatgen.analysis.structure_prediction.substitution_probability import (
    SubstitutionPredictor,
    SubstitutionProbability,
)
from pymatgen.core.periodic_table import Species
from pymatgen.util.testing import PymatgenTest


def get_table():
    """
    Loads a lightweight lambda table for use in unit tests to reduce
    initialization time, and make unit tests insensitive to changes in the
    default lambda table.
    """
    data_dir = os.path.join(
        PymatgenTest.TEST_FILES_DIR,
        "struct_predictor",
    )

    json_file = os.path.join(data_dir, "test_lambda.json")
    with open(json_file) as f:
        lambda_table = json.load(f)
    return lambda_table


class SubstitutionProbabilityTest(unittest.TestCase):
    def test_full_lambda_table(self):
        """
        This test tests specific values in the data folder. If the
        json is updated, these tests will have to be as well
        """
        sp = SubstitutionProbability(alpha=-5.0)
        sp1 = Species("Fe", 4)
        sp3 = Species("Mn", 3)
        prob1 = sp.prob(sp1, sp3)
        self.assertAlmostEqual(prob1, 1.69243954552e-05, 5, "probability isn't correct")
        sp2 = Species("Pt", 4)
        sp4 = Species("Pd", 4)
        prob2 = sp.prob(sp2, sp4)
        self.assertAlmostEqual(prob2, 4.7174906021e-05, 5, "probability isn't correct")
        corr = sp.pair_corr(Species("Cu", 2), Species("Fe", 2))
        self.assertAlmostEqual(corr, 6.82496631637, 5, "probability isn't correct")
        prob3 = sp.cond_prob_list([sp1, sp2], [sp3, sp4])
        self.assertAlmostEqual(prob3, 0.000300298841302, 6, "probability isn't correct")

    def test_mini_lambda_table(self):
        sp = SubstitutionProbability(lambda_table=get_table(), alpha=-5.0)
        o2 = Species("O", -2)
        s2 = Species("S", -2)
        li1 = Species("Li", 1)
        na1 = Species("Na", 1)
        self.assertAlmostEqual(sp.prob(s2, o2), 0.124342317272, 5, "probability isn't correct")
        self.assertAlmostEqual(sp.pair_corr(li1, na1), 1.65425296864, 5, "correlation isn't correct")
        prob = sp.cond_prob_list([o2, li1], [na1, li1])
        self.assertAlmostEqual(prob, 0.00102673915742, 5, "probability isn't correct")


class SubstitutionPredictorTest(unittest.TestCase):
    def test_prediction(self):
        sp = SubstitutionPredictor(threshold=8e-3)
        result = sp.list_prediction(["Na+", "Cl-"], to_this_composition=True)[5]
        cprob = sp.p.cond_prob_list(result["substitutions"].keys(), result["substitutions"].values())
        self.assertAlmostEqual(result["probability"], cprob)
        self.assertEqual(set(result["substitutions"].values()), {"Na+", "Cl-"})

        result = sp.list_prediction(["Na+", "Cl-"], to_this_composition=False)[5]
        cprob = sp.p.cond_prob_list(result["substitutions"].keys(), result["substitutions"].values())
        self.assertAlmostEqual(result["probability"], cprob)
        self.assertNotEqual(set(result["substitutions"].values()), {"Na+", "Cl-"})

        c = Composition({"Ag2+": 1, "Cl-": 2})
        result = sp.composition_prediction(c, to_this_composition=True)[2]
        self.assertEqual(set(result["substitutions"].values()), set(c.elements))
        result = sp.composition_prediction(c, to_this_composition=False)[2]
        self.assertEqual(set(result["substitutions"].keys()), set(c.elements))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
