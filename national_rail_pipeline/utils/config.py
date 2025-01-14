from typing import List, Optional, Dict
import logging

from dotenv import load_dotenv

from national_rail_pipeline.utils.parsers import YAMLParser, ArgParser
from national_rail_pipeline.utils.exceptions import NoFileSpecified


class Config:
    def __init__(
        self,
        application_name: str,
        description: str,
        arguments: Optional[List[str]] = None,
    ):
        self.application_name = application_name
        self.description = description
        self._command_line_parser: ArgParser = self._prepare_arg_parser(description)
        self._parse_args(arguments)
        self.command_line_args = self._command_line_parser.get_args()
        self.run_config = self._parse_yaml_config_and_apply_overwrites()
        self._logger = None
        self._load_dotenv(self.command_line_args.dotenv)

    def log_config(self):
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        self._logger.info("Config for: {}".format(self.application_name))
        self._logger.info("Description: {}".format(self.description))
        self._log_parsed_args()
        self._log_yaml()

    def _log_parsed_args(self) -> None:
        self._logger.info("Command Line Arguments:")
        for arg, value in sorted(vars(self.command_line_args).items()):
            self._logger.info(f"Argument - {arg}: {value}")

    def _log_yaml(self) -> None:
        self._logger.info("Yaml Configuration: {}".format(self.run_config))

    @staticmethod
    def _load_dotenv(dotenvpath: str = None) -> None:
        load_dotenv(dotenvpath)

    def _parse_args(self, arguments: Optional[List[str]] = None) -> None:
        self._command_line_parser.parse_args(arguments)

    @staticmethod
    def _prepare_arg_parser(description: Optional[str]) -> ArgParser:
        command_line_parser = ArgParser(description)

        command_line_parser.add_argument(
            "--config",
            "-c",
            default="config.yml",
            action="store",
            type=str,
            required=False,
            help="Defines the path of the file where the application is\
                  configured.",
        )

        command_line_parser.add_argument(
            "--dotenv",
            default=None,
            action="store",
            type=str,
            required=False,
            help="Defines the path of the dotenv file where the application is\
                  configured.",
        )

        command_line_parser.add_argument(
            "--debug",
            "-d",
            default=False,
            action="store_true",
            required=False,
            help="Defines whether the app should run in debug mode (Not\
                  recommended for production)",
        )

        command_line_parser.add_argument(
            "--logdir",
            "-l",
            default=None,
            action="store",
            type=str,
            required=False,
            help="The path where data is logged by the application",
        )

        return command_line_parser

    def _parse_yaml_config(self) -> Dict:
        try:
            return YAMLParser().read_yaml(
                filepath=self._command_line_parser.get_args().config
            )
        except NoFileSpecified:
            return {}

    def _parse_yaml_config_and_apply_overwrites(self) -> Dict:
        run_config = self._parse_yaml_config()
        # Overwrite Log Dir from cli arguments
        if self.command_line_args.logdir is not None:
            run_config["LOG_FILE_DIRECTORY"] = self.command_line_args.logdir
        return run_config
