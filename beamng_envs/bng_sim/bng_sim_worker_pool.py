import time

import numpy as np

from beamng_envs.bng_sim.bng_sim_worker import BNGSimWorker


class BNGSimWorkerPool:
    """Set and track state of currently active bng instances."""

    def __init__(self, user_path: str, n_workers: int, start_port: int = 58000):
        self.n_workers = n_workers
        self.workers = [
            BNGSimWorker(user_path=user_path, port=start_port + p)
            for p in range(n_workers)
        ]
        self.start_port = start_port

    def get_free_worker(self) -> BNGSimWorker:
        time.sleep(np.random.uniform(1, 2))
        worker = None
        while worker is None:
            for w in self.workers:
                if not w.busy:
                    worker = w
                break
            else:
                print(f"Bool busy, still looking for a worker.")
                time.sleep(np.random.uniform(1, 2))

        else:
            print(f"Worker: {worker} is free.")

        return worker
