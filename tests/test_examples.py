from biosimulators_utils.model_lang.xpp.validation import validate_model
import glob
import os
import unittest


class ExamplesTestCase(unittest.TestCase):
    FIXTURE_DIRNAME = os.path.join(os.path.dirname(__file__), 'fixtures')

    def test(self):
        for filename in glob.glob(os.path.join(self.FIXTURE_DIRNAME, '*.ode')):
            errors, _, _ = validate_model(filename)
            assert errors == []
