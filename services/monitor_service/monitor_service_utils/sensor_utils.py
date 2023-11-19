import os.path
from common.utils.service_utils import ServiceUtils


class SensorUtils:
    """This class should hold the utils that Sensor classes will be using"""

    @staticmethod
    def get_raw_config_dict() -> dict:
        from pathlib import Path
        parent_path = Path(__file__).parent.parent
        config_file_path = os.path.join(parent_path, "config.json")
        return ServiceUtils.load_local_json_file(file_path=config_file_path)

    @classmethod
    def get_config_dict(cls) -> dict:
        config_dict = cls.get_raw_config_dict()
        for sensor_dict in config_dict.pop("sensors"):
            sensor_config_type = sensor_dict["type"]
            config_dict.update({sensor_config_type: sensor_dict})
        return config_dict
