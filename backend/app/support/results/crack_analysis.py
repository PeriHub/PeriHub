import numpy as np
from exodusreader import exodusreader

from ..globals import log


class CrackAnalysis:

    @staticmethod
    def get_crack_length(file: str, step: int = -1):

        (
            points,
            point_data,
            global_data,
            cell_data,
            ns,
            block_data,
            time,
        ) = exodusreader.read_timestep(file, step)

        points_x = np.array(points[:, 0])
        points_y = np.array(points[:, 1])
        points_z = np.array(points[:, 2])
        damage = point_data["Damage"]

        damaged_points_x = points_x[damage != 0]
        damaged_points_y = points_y[damage != 0]
        damaged_points_z = points_z[damage != 0]

        if len(damaged_points_x) == 0:
            log.warning("No damaged points found")
            return 1, 1, time
        crack_y = damaged_points_y[np.argmin(damaged_points_x)]

        damaged_points_x = damaged_points_x[damaged_points_y == crack_y]

        crack_length = np.max(damaged_points_x) - np.min(damaged_points_x)

        crack_width = np.max(damaged_points_z) - np.min(damaged_points_z)

        return crack_length, crack_width, time
