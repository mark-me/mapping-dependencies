import os
from pathlib import Path

import yaml
from logtools import get_logger

logger = get_logger(__name__)


class ConfigFile:
    """Manages configuration settings from a TOML file.

    Reads and writes configuration data to a TOML file, providing access to settings
    like default file/directory paths, level colors, and export options.
    """

    def __init__(self, file_config: str):
        """Initialize the ConfigFile object.

        Sets up the configuration file path, initializes data, defines default settings,
        and reads the configuration from the file.
        """
        self._file = Path(file_config)
        self._data = self._read_file()

    def _read_file(self) -> dict:
        """Read and parse the configuration file.

        Reads the configuration from the YAML file, if it exists, and populates the internal data.
        If the file doesn't exist, it logs a warning.
        """
        config_data = {}
        if self._file.exists():
            with open(self._file) as f:
                config_data = yaml.safe_load(f)
        else:
            logger.error(f"Couldn't find config file '{self._file}'")
        return config_data

    def _create_output_dir(self, file_path: str) -> None:
        parent_directory = os.path.dirname(file_path)
        Path(parent_directory).mkdir(parents=True, exist_ok=True)

    @property
    def dir_intermediate_root(self) -> str:
        """Directory where all intermediate output is placed

        Returns the path to the default file specified in the configuration.
        """
        folder = os.path.join(
            self._data["folder_intermediate_root"],
            self._data["title"],
            str(self._data["version"]),
        )
        return folder

    @property
    def pd_files(self) -> list:
        """All Power Designer document paths

        Returns a list of Power Designer document paths
        """
        lst_pd_files = self._data["power-designer"]["files"]
        lst_pd_files = [
            Path(
                os.path.join(
                    self._data["folder_intermediate_root"],
                    self._data["power-designer"]["folder"],
                    pd_file,
                )
            )
            for pd_file in lst_pd_files
        ]
        return lst_pd_files

    @property
    def dir_RETW_output(self) -> str:
        folder = os.path.join(
            self.dir_intermediate_root, self._data["extractor"]["folder"]
        )
        self._create_output_dir(folder)
        return folder
