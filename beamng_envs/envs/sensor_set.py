import copy
from dataclasses import dataclass
from typing import Dict, Any

from beamngpy import Vehicle
from beamngpy.sensors import State, Electrics, GForces, Damage, Sensor


@dataclass
class SensorSet:
    """Handles the basic sensor classes and .tech."""

    include_tech_sensors: bool = False

    @property
    def basic_sensors(self) -> Dict[str, Sensor]:
        """Return the basic sensors available in BeamNG.drive."""
        return dict(
            state=State(),
            electrics=Electrics(),
            g_forces=GForces(),
            damage=Damage(),
            # imu=IMU(pos=(0, 0, 0), name='imu'),  # Causing LUA error on attach
        )

    @property
    def advanced_sensors(self) -> Dict[str, Sensor]:
        """TODO: Return the advanced sensors only available in BeamNG.tech."""
        return {}

    @property
    def sensors(self) -> Dict[str, Sensor]:
        """Return currently active sensors."""
        sensors = self.basic_sensors
        if self.include_tech_sensors:
            sensors.update(self.advanced_sensors)

        return sensors

    def attach_to_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Attach the managed sensors to a vehicle."""
        current_sensors = [s[0] for s in vehicle.sensors.items()]
        for sensor_name, sensor in self.sensors.items():
            if sensor_name not in current_sensors:
                vehicle.sensors.attach(sensor_name, sensor)

        return vehicle

    def poll_for_vehicle(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Poll the sensors for a vehicle in the simulation."""
        vehicle.sensors.poll()
        sensor_data = copy.deepcopy(
            {k: vehicle.sensors[k].data for k in self.sensors.keys()}
        )

        return sensor_data
