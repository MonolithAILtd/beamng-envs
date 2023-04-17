from gym.spaces import Dict, Box

TRACK_TEST_PARAM_SPACE = dict(
    brake_strength=dict(
        values=(0.6, 1),
        name="$brakestrength",
        description="Break force multiplier 60-100%",
        type=float,
        default=0.6,
    ),
    brake_bias=dict(
        values=(0, 1),
        name="$brakebias",
        description="Front/rear brake bias 0-100%",
        type=float,
        default=0.55,
    ),
    spoiler_angle_r=dict(
        values=(8, 20),
        name="$spoiler_angle_r",
        description="Rear wing angle, degrees 8-20",
        type=float,
        default=10,
    ),
    camber_f=dict(
        values=(0.95, 1),
        name="$camber_F",
        description="Front wheel camber",
        type=float,
        default=0.975,
    ),
    camber_r=dict(
        values=(0.95, 1),
        name="$camber_R",
        description="Rear wheel camber",
        type=float,
        default=0.965,
    ),
    toe_f=dict(
        values=(0.95, 1),
        name="$toe_F",
        description="Front wheel toe",
        type=float,
        default=0.977,
    ),
    toe_r=dict(
        values=(0.95, 1),
        name="$toe_R",
        description="Rear wheel toe",
        type=float,
        default=0.984,
    ),
    tire_pressure_f=dict(
        values=(0, 50),
        name="$tirepressure_F",
        description="Front tire pressure, psi",
        type=float,
        default=28.0,
    ),
    tire_pressure_r=dict(
        values=(0, 50),
        name="$tirepressure_R",
        description="Rear tire pressure, psi",
        type=float,
        default=27.06,
    ),
    driver_aggression=dict(
        values=(0.75, 1.25),
        name="driver_aggression",
        description="Aggressiveness setting of AI driver",
        type=float,
        default=1,
    ),
)

TRACK_TEST_PARAM_SPACE_GYM = Dict(
    {
        v["name"]: Box(low=v["values"][0], high=v["values"][1])
        for v in TRACK_TEST_PARAM_SPACE.values()
    }
)
