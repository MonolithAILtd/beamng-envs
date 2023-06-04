import tempfile
import unittest

from beamng_envs.bng_sim.bng_sim_worker import BNGSimWorker
from beamng_envs.bng_sim.bng_sim_worker_pool import BNGSimWorkerPool
from tests.common.tidy_test_case import TidyTestCase


class TestBNGSimWorkerPool(TidyTestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        self._sut = BNGSimWorkerPool(n_workers=2, user_path=self._tmp_dir.name)

    def test_get_free_worker(self):
        # Act
        worker = self._sut.get_free_worker()

        # Assert
        self.assertIsInstance(worker, BNGSimWorker)
