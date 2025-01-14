import os.path
from typing import List, Optional, Any, Dict

from argparse import ArgumentParser, Namespace, Action
import yaml

from national_rail_pipeline.utils.exceptions import InvalidConfigError, NoFileSpecified


READ = "r"


class ArgParser:
    def __init__(self, description: str):
        self.arg_parser = ArgumentParser(description=description)
        self._parsed_args: Namespace = Namespace()

    def parse_args(self, arguments: Optional[List[str]] = None) -> None:
        self._parsed_args = self.arg_parser.parse_args(arguments)

    def add_argument(self, *args: Any, **kwargs: Any) -> Action:
        return self.arg_parser.add_argument(*args, **kwargs)

    def get_args(self) -> Namespace:
        return self._parsed_args


class YAMLParser:
    def read_yaml(self, filepath: str) -> Dict[str, Any]:

        if filepath is None:
            raise NoFileSpecified

        if os.path.exists(filepath):
            parsed_yaml = self._do_read_yaml(filepath)
            return parsed_yaml

        raise FileNotFoundError(f"yaml file does not exist! Expected path: {filepath}")

    @staticmethod
    def _do_read_yaml(filepath: str) -> Dict[str, Any]:
        yaml_file = open(filepath, READ)
        try:
            parsed_yaml = yaml.safe_load(yaml_file)
            yaml_file.close()
            return parsed_yaml
        except yaml.YAMLError as err:
            raise InvalidConfigError(str(err))
