import tempfile
import unittest


class TidyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        try:
            self._tmp_dir.cleanup()
        except OSError:
            pass
