import os
from pathlib import Path

import yaml

from logtools import get_logger

from .config_data import (
    ConfigData,
    DevOpsConfig,
    ExtractorConfig,
    GeneratorConfig,
    PowerDesignerConfig,
    PublisherConfig,
)

logger = get_logger(__name__)


class ConfigFileError(Exception):
    """Exception raised for configuration file errors."""

    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Code: {self.error_code})"


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
        self._expected_structure = {
            "title": {},
            "folder_intermediate_root": {},
            "power-designer": {"folder": str, "files": list},
            "extractor": {"bla": str},
            "generator": {},
            "publisher": {},
            "devops": {},
        }
        self._data: ConfigData = self._read_file()
        self._version = self._determine_version()

    def _read_file(self) -> ConfigData:
        """Read and parse the configuration file.

        Reads the configuration from the YAML file, if it exists, and populates the internal data.
        If the file doesn't exist, it logs a warning.
        """
        if not self._file.exists():
            msg = f"Couldn't find config file '{self._file}'"
            logger.error(msg)
            raise ConfigFileError(msg, 400)

        with open(self._file) as f:
            config_raw = yaml.safe_load(f)

        if not isinstance(config_raw, dict):
            raise ConfigFileError("Configuratiebestand is leeg of ongeldig.", 401)

        # Verplichte toplevel velden
        for key in ["title", "folder_intermediate_root"]:
            if key not in config_raw:
                raise ConfigFileError(
                    f"Verplichte configuratiesleutel ontbreekt: {key}", 402
                )

        # Default substructuren
        defaults = {
            "power-designer": {"folder": "", "files": []},
            "extractor": {"folder": "RETW"},
            "generator": {
                "folder": "",
                "templates_platform": None,
                "created_ddls_json": None,
            },
            "publisher": {
                "vs_project_folder": "",
                "vs_project_file": "",
                "codeList_json": "",
                "codeList_folder": "",
                "mdde_scripts_folder": "",
            },
            "devops": {
                "organisation": "",
                "project": "",
                "repo": "",
                "branch": "",
                "work_item": "",
                "work_item_description": "",
            },
        }

        for section, values in defaults.items():
            config_raw.setdefault(section, values)

        config_raw["power_designer"] = config_raw.pop("power-designer")

        return ConfigData(
            title=config_raw["title"],
            folder_intermediate_root=config_raw["folder_intermediate_root"],
            power_designer=PowerDesignerConfig(**config_raw["power_designer"]),
            extractor=ExtractorConfig(**config_raw["extractor"]),
            generator=GeneratorConfig(**config_raw["generator"]),
            publisher=PublisherConfig(**config_raw["publisher"]),
            devops=DevOpsConfig(**config_raw["devops"]),
        )

    def _verify_dict(self, to_check: dict, keys_required: list):
        if missing := [k for k in keys_required if k not in to_check]:
            msg = f"Ontbrekende configuratie item(s): {', '.join(missing)}"
            raise ConfigFileError(msg, 206)

    def _verify_file_content(self, data_file: dict) -> bool:
        """Verify the content of the configuration file.

        Checks if all required keys are present in the provided data.
        Raises a ConfigFileError if any required keys are missing.
        """
        required_keys = self._expected_structure.keys()
        self._verify_dict(data_file, self._expected_structure)
        for key in required_keys:
            if len(data_file[key]) > 0:
                required_keys = self._expected_structure[key].keys()
                self._verify_dict(data_file[key], self._expected_structure)

    def _create_dir(self, dir_path: Path) -> None:
        """Create a directory if it doesn't exist.

        Creates the specified directory, including any necessary parent directories.
        If the provided path is a file, it extracts the directory part.
        """
        if dir_path.is_file():
            dir_path = os.path.dirname(dir_path)
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    def _determine_version(self) -> str:
        """Determine the version for the output folder.

        Determines the version string by checking existing version folders and incrementing the patch number.
        Creates the output folder with the determined version.
        """
        version = "v00.00.01"
        folder = Path(
            os.path.join(
                self._data.folder_intermediate_root,
                self._data.title,
            )
        )
        if folder.exists():
            if lst_versions := [
                version for version in folder.iterdir() if version.is_dir()
            ]:
                # Extract version numbers, sort them, and increment the latest
                versions = sorted(
                    [v.name for v in lst_versions if v.name.startswith("v")],
                    key=lambda s: list(map(int, s[1:].split("."))),
                )
                latest_version = versions[-1]
                major, minor, patch = map(int, latest_version[1:].split("."))
                patch += 1
                version = f"v{major:02}.{minor:02}.{patch:02}"
        folder = Path(os.path.join(folder, version))
        self._create_dir(dir_path=folder)

    @property
    def dir_intermediate_root(self) -> str:
        """Directory where all intermediate output is placed

        Returns the path to the default file specified in the configuration.
        """
        folder = os.path.join(
            self._data.folder_intermediate_root,
            self._data.title,
            str(self._version),
        )
        return folder

    @property
    def pd_files(self) -> list:
        """All Power Designer document paths

        Returns a list of Power Designer document paths
        """
        lst_pd_files = self._data.power_designer.files
        lst_pd_files = [
            Path(
                os.path.join(
                    self._data.folder_intermediate_root,
                    self._data.power_designer.folder,
                    pd_file,
                )
            )
            for pd_file in lst_pd_files
        ]
        return lst_pd_files

    @property
    def dir_RETW_output(self) -> str:
        folder = Path(
            os.path.join(self.dir_intermediate_root, self._data.extractor.folder)
        )
        self._create_dir(folder)
        return folder
