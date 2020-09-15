#!/usr/bin/env python
"""
This module proposes unit tests for the run_experiment module.
"""

import os
import unittest
from unittest.mock import patch
from pathlib import Path

from typer.testing import CliRunner

from bb_wrapper.run_experiment import cli, run

CONFIG = Path(__file__).parent / "test_config" / "vanilla.yaml"
SBATCH = Path(__file__).parent / "test_sbatch" / "test_sbatch.sbatch"


runner = CliRunner()


class TestShamanExperiment(unittest.TestCase):

    @patch('bb_wrapper.shaman_experiment.SHAManExperiment.launch')
    @patch('bb_wrapper.shaman_experiment.SHAManExperiment.end')
    def test_run_experiment(self, mock_launch, mock_end):
        """Tests that running the SHAMan experiment works as expected.
        """
        run(
            component_name="component_1",
            nbr_iteration=10,
            sbatch_file=SBATCH,
            experiment_name="test_experiment",
            configuration_file=CONFIG,
            sbatch_dir=None,
            slurm_dir=None,
            result_file=None
        )
        assert not list(Path.cwd().glob("slurm*.out"))
        assert not list(Path.cwd().glob("*_shaman.sbatch"))

    @patch('bb_wrapper.shaman_experiment.SHAManExperiment.launch')
    @patch('bb_wrapper.shaman_experiment.SHAManExperiment.end')
    def test_main_cli(self, mock_launch, mock_end):
        """ Test the shaman CLI runs properly """
        args_list = ['--component-name', 'component_1',
                     '--nbr-iteration', '3',
                     '--sbatch-file', SBATCH,
                     '--experiment-name', 'test_experiment',
                     '--configuration-file', CONFIG]
        result = runner.invoke(cli, args_list)
        assert result.exit_code == 0
        assert "experiment test_experiment" in result.stdout
        assert not list(Path.cwd().glob("slurm*.out"))
        assert not list(Path.cwd().glob("*_shaman.sbatch"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
