from biosimulators_utils.model_lang.xpp.data_model import SIMULATION_METHOD_KISAO_MAP
from biosimulators_utils.model_lang.xpp.validation import validate_model
from biosimulators_utils.sedml.data_model import (
    ModelAttributeChange, UniformTimeCourseSimulation,
    Algorithm, AlgorithmParameterChange,
    Variable, Symbol)
from biosimulators_utils.warnings import BioSimulatorsWarning
from biosimulators_xpp import get_simulator_version
from biosimulators_xpp import utils
from kisao.exceptions import AlgorithmCannotBeSubstitutedException
from kisao.warnings import AlgorithmSubstitutedWarning
from unittest import mock
import numpy.testing
import os
import shutil
import tempfile
import unittest


class UtilsTestCase(unittest.TestCase):
    FIXTURES_DIRNAME = os.path.join(os.path.dirname(__file__), 'fixtures')

    def setUp(self):
        self.dirname = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_get_simulator_version(self):
        self.assertEqual(get_simulator_version(), '8.0')

        with mock.patch('subprocess.run', return_value=mock.Mock(returncode=1, stdout=mock.Mock(decode=lambda encoding: 'msg'))):
            with self.assertRaises(RuntimeError):
                get_simulator_version()

    def test_get_simulation_method_kisao_map(self):
        self.assertEqual(utils.get_simulation_method_kisao_map(), SIMULATION_METHOD_KISAO_MAP)

    def test_validate_variables(self):
        model = {
            'initial_conditions': {
                'U': 0.1,
                'V': 0.05,
            },
        }

        vars = [
            Variable(symbol=Symbol.time.value),
            Variable(target='u'),
            Variable(target='V'),
        ]

        utils.validate_variables(model, vars)

        vars[0].symbol = 'undefined'
        with self.assertRaises(NotImplementedError):
            utils.validate_variables(model, vars)

        vars[0].symbol = None
        vars[0].target = 'w'
        with self.assertRaises(ValueError):
            utils.validate_variables(model, vars)

    def test_apply_model_changes(self):
        filename = os.path.join(self.FIXTURES_DIRNAME, 'wilson-cowan.ode')
        _, _, xpp_model = validate_model(filename)

        sed_model_changes = [
            ModelAttributeChange(target='parameters.aee', new_value='12'),
            ModelAttributeChange(target='initialConditions.U', new_value='0.2'),
        ]
        utils.apply_model_changes(xpp_model, sed_model_changes)

        self.assertEqual(xpp_model['parameters']['aee'], '12')
        self.assertEqual(xpp_model['initial_conditions']['U'], '0.2')

        sed_model_changes = [
            ModelAttributeChange(target='parameters.AEE', new_value='14'),
            ModelAttributeChange(target='initialConditions.u', new_value='0.25'),
        ]
        utils.apply_model_changes(xpp_model, sed_model_changes)

        self.assertEqual(xpp_model['parameters']['aee'], '14')
        self.assertEqual(xpp_model['initial_conditions']['U'], '0.25')

        sed_model_changes = [
            ModelAttributeChange(target='parameters.AEE', new_value=14),
            ModelAttributeChange(target='initialConditions.u', new_value=0.25),
        ]
        utils.apply_model_changes(xpp_model, sed_model_changes)

        self.assertEqual(xpp_model['parameters']['aee'], 14)
        self.assertEqual(xpp_model['initial_conditions']['U'], 0.25)

        sed_model_changes = [
            ModelAttributeChange(target='unknown.AEE', new_value='13'),
        ]
        with self.assertRaises(ValueError):
            utils.apply_model_changes(xpp_model, sed_model_changes)

        sed_model_changes = [
            ModelAttributeChange(target='parameters.unknown', new_value='13'),
        ]
        with self.assertRaises(ValueError):
            utils.apply_model_changes(xpp_model, sed_model_changes)

        sed_model_changes = [
            ModelAttributeChange(target='initialConditionss.unknown', new_value='13'),
        ]
        with self.assertRaises(ValueError):
            utils.apply_model_changes(xpp_model, sed_model_changes)

    def test_set_up_simulation(self):
        filename = os.path.join(self.FIXTURES_DIRNAME, 'wilson-cowan.ode')
        _, _, xpp_sim = validate_model(filename)

        sed_sim = UniformTimeCourseSimulation(
            initial_time=10.,
            output_start_time=20.,
            output_end_time=30.,
            number_of_points=10,
            algorithm=Algorithm(
                kisao_id='KISAO_0000019',
                changes=[
                    AlgorithmParameterChange(kisao_id='KISAO_0000209', new_value='1e-8'),
                    AlgorithmParameterChange(kisao_id='KISAO_0000211', new_value='1e-6'),
                ],
            )
        )

        utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

        self.assertEqual(xpp_sim['simulation_method'], {
            't0': '10.0',
            'total': '20.0',
            'dt': '1.0',
            'njmp': '1',
            'meth': 'cvode',
            'toler': '1e-8',
            'atoler': '1e-6',
        })
        self.assertEqual(xpp_sim['plot'], {
            'elements': {
                1: {
                    'x': 'U',
                    'y': 'V',
                },
            },
            'xlo': -.1,
            'xhi': 1,
            'ylo': -.1,
            'yhi': 1,
        })

        utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

        sed_sim = UniformTimeCourseSimulation(
            initial_time=10.,
            output_start_time=20.,
            output_end_time=30.,
            number_of_points=10,
            algorithm=Algorithm(
                kisao_id='KISAO_0000032',
                changes=[
                ],
            )
        )
        utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])
        self.assertEqual(xpp_sim['simulation_method'], {
            't0': '10.0',
            'total': '20.0',
            'dt': '1.0',
            'njmp': '1',
            'meth': 'rungekutta',
        })

        # algorithm substitution
        xpp_sim['simulation_method']['meth'] = 'cvode'

        sed_sim = UniformTimeCourseSimulation(
            initial_time=10.,
            output_start_time=20.,
            output_end_time=30.,
            number_of_points=10,
            algorithm=Algorithm(
                kisao_id='KISAO_0000560',
                changes=[
                ],
            )
        )
        with mock.patch.dict(os.environ, {'ALGORITHM_SUBSTITUTION_POLICY': 'NONE'}):
            with self.assertRaises(AlgorithmCannotBeSubstitutedException):
                utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

        with mock.patch.dict(os.environ, {'ALGORITHM_SUBSTITUTION_POLICY': 'SIMILAR_APPROXIMATIONS'}):
            with self.assertWarns(AlgorithmSubstitutedWarning):
                utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

        self.assertEqual(xpp_sim['simulation_method'], {
            't0': '10.0',
            'total': '20.0',
            'dt': '1.0',
            'njmp': '1',
            'meth': 'rungekutta',
        })

        # algorithm substitution - parameters
        sed_sim = UniformTimeCourseSimulation(
            initial_time=10.,
            output_start_time=20.,
            output_end_time=30.,
            number_of_points=10,
            algorithm=Algorithm(
                kisao_id='KISAO_0000019',
                changes=[
                    AlgorithmParameterChange(kisao_id='KISAO_0000209', new_value='1e-8'),
                    AlgorithmParameterChange(kisao_id='KISAO_0000488', new_value='1e-8'),
                ],
            )
        )

        with mock.patch.dict(os.environ, {'ALGORITHM_SUBSTITUTION_POLICY': 'NONE'}):
            with self.assertRaises(NotImplementedError):
                utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

        with mock.patch.dict(os.environ, {'ALGORITHM_SUBSTITUTION_POLICY': 'SIMILAR_APPROXIMATIONS'}):
            with self.assertWarns(BioSimulatorsWarning):
                utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

    def test_write_xpp_parameter_file(self):
        filename = os.path.join(self.dirname, 'model.par')
        utils.write_xpp_parameter_file({
            'aee': '10',
            'aie': '8',
        }, filename)
        self.assertTrue(os.path.isfile(filename))

        filename = os.path.join(self.dirname, 'model2.par')
        utils.write_xpp_parameter_file({
            'aee': 10,
            'aie': 8,
        }, filename)
        self.assertTrue(os.path.isfile(filename))

    def test_write_xpp_initial_conditions_file(self):
        filename = os.path.join(self.dirname, 'model.ic')
        utils.write_xpp_initial_conditions_file({
            'U': '0.2',
            'V': '0.1',
        }, filename)
        self.assertTrue(os.path.isfile(filename))

        filename = os.path.join(self.dirname, 'model2.ic')
        utils.write_xpp_initial_conditions_file({
            'U': 0.2,
            'V': 0.1,
        }, filename)
        self.assertTrue(os.path.isfile(filename))

    def test_write_method_to_xpp_simulation_file(self):
        in_filename = os.path.join(self.FIXTURES_DIRNAME, 'wilson-cowan.ode')
        out_filename = os.path.join(self.dirname, 'modified.ode')
        utils.write_method_to_xpp_simulation_file({
            'meth': 'cvode',
            't0': 10,
            'total': 100,
            'dt': 0.1,
            'njmp': 10,
        }, in_filename, out_filename)

        errors, _, model = validate_model(in_filename)
        errors2, _, model2 = validate_model(out_filename)
        self.assertEqual(errors, [])
        self.assertEqual(errors2, [])

        self.assertEqual(model['simulation_method'], {
            'total': '40',
        })
        self.assertEqual(model['plot'], {
            'elements': {
                1: {
                    'x': 'U',
                    'y': 'V',
                },
            },
            'xlo': -.1,
            'xhi': 1,
            'ylo': -.1,
            'yhi': 1,
        })
        self.assertEqual(model2['simulation_method'], {
            'meth': 'cvode',
            'total': '100',
            't0': '10',
            'dt': '0.1',
            'njmp': '10',
        })

    def test_exec_xpp_simulation(self):
        filename = os.path.join(self.FIXTURES_DIRNAME, 'wilson-cowan.ode')
        errors, _, model = validate_model(filename)
        self.assertEqual(errors, [])
        results = utils.exec_xpp_simulation(filename, model)
        self.assert_results(model, results)

        model['t0'] = 10.
        model['total'] = 50.
        model['dt'] = 0.1
        model['njmp'] = 10.
        results = utils.exec_xpp_simulation(filename, model)
        self.assert_results(model, results)

        with mock.patch('subprocess.run', return_value=mock.Mock(returncode=1, stdout=mock.Mock(decode=lambda encoding: 'msg'))):
            with self.assertRaises(RuntimeError):
                results = utils.exec_xpp_simulation(filename, model)

    def assert_results(self, model, results):
        t0 = float(model['simulation_method'].get('t0', 0.))
        duration = float(model['simulation_method'].get('total', 20.))
        dt = float(model['simulation_method'].get('dt', 0.05))
        njmp = float(model['simulation_method'].get('njmp', 1))
        numpy.testing.assert_allclose(
            results.loc[:, Symbol.time.value],
            numpy.linspace(
                t0,
                t0 + duration,
                round(duration / (dt * njmp)) + 1
            ))

        for column in results.columns:
            self.assertFalse(numpy.any(numpy.isnan(results.loc[:, column])))

    def test_get_results_of_sed_variables(self):
        filename = os.path.join(self.FIXTURES_DIRNAME, 'wilson-cowan.ode')
        _, _, xpp_sim = validate_model(filename)

        sed_sim = UniformTimeCourseSimulation(
            initial_time=10.,
            output_start_time=20.,
            output_end_time=30.,
            number_of_points=20,
            algorithm=Algorithm(
                kisao_id='KISAO_0000032',
            )
        )

        utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])
        self.assertEqual(xpp_sim['simulation_method']['t0'], '10.0')
        self.assertEqual(xpp_sim['simulation_method']['total'], '20.0')
        self.assertEqual(xpp_sim['simulation_method']['dt'], '0.5')
        self.assertEqual(xpp_sim['simulation_method']['njmp'], '1')

        xpp_results = utils.exec_xpp_simulation(filename, xpp_sim)
        numpy.testing.assert_allclose(xpp_results.loc[:, Symbol.time.value],
                                      numpy.linspace(10., 30., 40 + 1))

        sed_vars = [
            Variable(id='time', symbol=Symbol.time.value),
            Variable(id='u_lower', target='u'),
            Variable(id='u_upper', target='U'),
            Variable(id='v_lower', target='v'),
            Variable(id='v_upper', target='V'),
        ]
        var_results = utils.get_results_of_sed_variables(sed_sim, xpp_results, sed_vars)

        numpy.testing.assert_allclose(var_results['time'],
                                      numpy.linspace(20., 30., 20 + 1))

        numpy.testing.assert_allclose(var_results['u_lower'], var_results['u_upper'])
        numpy.testing.assert_allclose(var_results['v_lower'], var_results['v_upper'])
        self.assertFalse(numpy.any(numpy.isnan(var_results['u_lower'])))
        self.assertFalse(numpy.any(numpy.isnan(var_results['v_lower'])))

    def test_xpp_from_sbml_format_converter(self):
        filename = os.path.join(self.FIXTURES_DIRNAME, 'BIOMD0000000001.ode')
        _, _, xpp_sim = validate_model(filename)

        sed_sim = UniformTimeCourseSimulation(
            initial_time=0.,
            output_start_time=0.,
            output_end_time=10.,
            number_of_points=100,
            algorithm=Algorithm(
                kisao_id='KISAO_0000019',
            )
        )

        utils.set_up_simulation(sed_sim, xpp_sim['simulation_method'])

        xpp_results = utils.exec_xpp_simulation(filename, xpp_sim)
