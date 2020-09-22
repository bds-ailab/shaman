"""Tests the proper integration of slurm components within Slurm, for the submit_sbatch method.
"""
import unittest
from pathlib import Path
import time
from bb_wrapper.tunable_component.component import TunableComponent


MODULE_CONFIGURATION = Path(__file__).parent / \
    "test_config" / "component_config.yaml"
TEST_SBATCH = Path(__file__).parent / \
    "test_sbatch" / "test_sbatch.sbatch"


class TestTunableComponent(unittest.TestCase):
    """Tests that component tuning works as expected when integrated with Slurm.
    """

    def test_submit_sbatch_wait(self):
        """Tests that the sbatch submission works as expected, when wait is enabled.
        """
        tunable_component = TunableComponent(
            "component_1", MODULE_CONFIGURATION)
        start = time.time()
        job_id = tunable_component.submit_sbatch(TEST_SBATCH, wait=True)
        end = time.time()
        assert isinstance(job_id, int)
        self.assertGreater(end - start, 10)

    def test_submit_sbatch_no_wait(self):
        """Tests that the sbatch submission works as expected, when wait is not enabled.
        """
        tunable_component = TunableComponent(
            "component_1", MODULE_CONFIGURATION)
        start = time.time()
        job_id = tunable_component.submit_sbatch(TEST_SBATCH, wait=False)
        end = time.time()
        assert isinstance(job_id, int)
        self.assertLess(end - start, 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
