import json


class ServiceUtils:

    @staticmethod
    def load_local_json_file(file_path: str) -> dict:
        with open(file_path, "r") as config_file:
            string_content = config_file.read()
        return json.loads(string_content)
