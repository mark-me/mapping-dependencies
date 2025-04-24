from dataclasses import dataclass, field
from typing import List

@dataclass
class PowerDesignerConfig:
    """Configuration settings for PowerDesigner.

    Holds the folder path and a list of PowerDesigner file names.
    """
    folder: str
    files: List[str] = field(default_factory=list)

@dataclass
class ExtractorConfig:
    """Configuration settings for the Extractor.

    Specifies the folder for extractor output.
    """
    folder: str = "RETW"

@dataclass
class GeneratorConfig:
    """Configuration settings for the Generator.

    Specifies the output folder, platform templates, and JSON file for created DDLs.
    """
    templates_platform: str
    folder: str = "Generator"
    created_ddls_json: str = "ddls.json"

@dataclass
class PublisherConfig:
    """Configuration settings for the Publisher.

    Specifies various paths and settings related to publishing, including Visual Studio project details, code lists, and MDDE scripts.
    """
    vs_project_folder: str
    vs_project_file: str
    codeList_json: str
    codeList_folder: str
    mdde_scripts_folder: str

@dataclass
class DevOpsConfig:
    """Configuration settings for DevOps.

    Specifies details for DevOps integration, including organization, project, repository, branch, and work item information.
    """
    organisation: str
    project: str
    repo: str
    branch: str
    work_item: str
    work_item_description: str

@dataclass
class ConfigData:
    """Overall configuration settings.

    Combines all configuration settings for different components of the application.
    """
    title: str
    folder_intermediate_root: str
    power_designer: PowerDesignerConfig = field(default_factory=PowerDesignerConfig)
    extractor: ExtractorConfig = field(default_factory=ExtractorConfig)
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    publisher: PublisherConfig = field(default_factory=PublisherConfig)
    devops: DevOpsConfig = field(default_factory=DevOpsConfig)

