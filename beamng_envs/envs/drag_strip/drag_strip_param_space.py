from gym.spaces import Dict, Text

from beamng_envs.cars.sunburst import PART_OPTIONS

DRAG_STRIP_PARAM_SPACE = {
    k: dict(values=v, name=k, descrition="A Sunburst car part.", type=str)
    for k, v in PART_OPTIONS.items()
}

DRAG_STRIP_PARAM_SPACE_GYM = Dict(
    {
        v["name"]: Text(min_length=1, max_length=1, charset=v["values"])
        for v in DRAG_STRIP_PARAM_SPACE.values()
    }
)
