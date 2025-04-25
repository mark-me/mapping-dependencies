import os
import sys
from pathlib import Path

from .config_file import ConfigFile

# from dependencies_checker import DagReporting
# from generator import DevOpsHandler, DDLGenerator, DDLPublisher
# from pd_extractor import PDDocument
from logtools import get_logger, issue_tracker

logger = get_logger(__name__)


class Orchestrator:
    """Orkestreert de Power Designer extractie en deployment workflow.

    Manages the extraction of data, dependency checking, code generation, and repository interactions.
    """
    def __init__(self, file_config: str):
        """Initialiseert de Orkestrator.

        Sets up the configuration based on the provided file path.

        Args:
            file_pd_ldm (Path): Locatie Power Designer ldm bestand
        """
        self.file_config = Path(file_config)
        self.config = ConfigFile(file_config=self.file_config)
        logger.info(f"Genesis geïnitialiseerd met configuratie uit '{file_config}'")

    def extract(self, file_pd_ldm: Path) -> str:
        """Extract data from a PowerDesigner LDM file.

        Extracts the logical data model and mappings from the specified file and saves them as a JSON file.

        Args:
            file_pd_ldm (Path): Locatie Power Designer ldm bestand

        Returns:
            None
        """
        logger.info(f"Start extraction for '{file_pd_ldm}'")
        # document = PDDocument(file_pd_ldm=file_pd_ldm)
        dir_output = self.config.dir_extract
        file_RETW = Path(os.path.join(dir_output, f"{file_pd_ldm.stem}.json"))
        # document.write_result(file_output=file_RETW)
        logger.info(
            f"Het logisch data model en mappings van '{file_pd_ldm}' geëxtraheerd en geschreven naar '{file_RETW}'"
        )
        return file_RETW

    def check_dependencies(self, files_RETW: list) -> None:
        """Check dependencies between extracted data files.

        Analyzes the relationships and dependencies between the extracted data.

        Args:
            files_RETW (list): A list of paths to the extracted RETW files.

        Returns:
            None
        """
        logger.info("Reporting on dependencies")
        # dag = DagReporting()
        # dag.add_RETW_files(files_RETW=lst_files_RETW)

    def generate_code(self, files_RETW: list) -> None:
        """Generate deployment code based on extracted data.

        Generates the necessary code for deployment based on the extracted data and dependencies.

        Args:
            files_RETW (list): A list of paths to the extracted RETW files.

        Returns:
            None
        """
        logger.info("Start generating deployment code")
        dir_output = self.config.dir_generate
        dir_output
        # Create stuff


    def clone_repository(self) -> str:
        """Clone the target repository.

        Clones the repository specified in the configuration to a local directory.

        Returns:
            str: The path to the cloned repository.
        """
        # devops_handler = DevOpsHandler(
        #     self.config.devops_config
        # )
        folder = ""
        return folder

    def start_processing(self, skip_deployment: bool = False) -> None:
        """Start the main processing workflow.

        Orchestrates the extraction, dependency checking, and deployment code generation.

        Args:
            skip_deployment (bool): Skip the deployment.

        Returns:
            None
        """
        logger.info("Start Genesis verwerking")
        lst_files_RETW = []
        for pd_file in self.config.files_power_designer:
            file_RETW = self.extract(file_pd_ldm=pd_file)
            lst_files_RETW.append(file_RETW)

        self.check_dependencies(files_RETW=lst_files_RETW)

        # Stop process if extraction and dependecies check result in issues
        if issue_tracker.has_issues():
            file_issues = os.path.join(self.config.dir_extract, "extraction_issues.csv")
            issue_tracker.write_csv(file_csv=file_issues)
            logger.error(f"Problemen gevonden, rapport is te vinden in {file_issues}")
            sys.exit("Verwerking gestopt nadat er issues zijn aangetroffen")

        self.generate_code(files_RETW=lst_files_RETW)
