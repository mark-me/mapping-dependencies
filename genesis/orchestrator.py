import os
import sys
from pathlib import Path

from genesis import ConfigFile

# from dependencies_checker import DagReporting
# from generator import DevOpsHandler, DDLGenerator, DDLPublisher
# from pd_extractor import PDDocument
from logtools import get_logger, issue_tracker

logger = get_logger(__name__)


class Genesis:
    def __init__(self, file_config: str):
        self.file_config = Path(file_config)
        self.config = ConfigFile(file_config=self.file_config)
        logger.info(f"Genesis geïnitialiseerd met configuratie uit '{file_config}'")

    def extract(self, file_pd_ldm: Path) -> str:
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
        logger.info("Reporting on dependencies")
        # dag = DagReporting()
        # dag.add_RETW_files(files_RETW=lst_files_RETW)

    def generate_deployment(self, files_RETW: list) -> None:
        logger.info("Start generating deployment code")
        dir_output = self.config.dir_generate
        dir_output
        # Create stuff


    def clone_repository(self) -> str:
        # devops_handler = DevOpsHandler(
        #     self.config.devops_config
        # )
        folder = ""
        return folder

    def start_processing(self):
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

        self.generate_deployment(files_RETW=lst_files_RETW)
