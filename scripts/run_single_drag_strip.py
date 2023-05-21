"""
Run the DragStrip environment a number of times, load and compare results.
"""
from beamngpy import BeamNGpy
from matplotlib import pyplot as plt

from beamng_envs.beamng_config import BeamNGConfig
from beamng_envs.envs.drag_strip.drag_strip_config import DragStripConfig
from beamng_envs.envs.drag_strip.drag_strip_env import DragStripEnv
from scripts.args_single import PARSER_SINGLE

N_RUNS = 5

if __name__ == "__main__":

    opt = PARSER_SINGLE.parse_args()

    config_ = DragStripConfig(
        bng_config=BeamNGConfig(
            home=opt.beamng_path,
            user=opt.beamng_user_path,
        ),
        bng_fps=30,
        max_time=30,
        bng_close_on_done=False,
        error_on_out_of_time=False
    )
    bng = BeamNGpy(**config_.bng_config.__dict__)

    for run in range(N_RUNS):
        env = DragStripEnv(
            params=DragStripEnv.param_space.sample(),
            config=config_,
            bng=bng
        )
        env.run()
        plt.plot(
            env.history['time_s'],
            [t['state']['pos'][0] for t in env.history['car_state']],
            label=f"run {run}"
        )

    plt.xlabel('Time')
    plt.ylabel('Distance travelled')
    plt.legend()
    plt.show()

    bng.close()
