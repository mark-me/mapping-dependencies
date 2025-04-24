import os
import sys
from pathlib import Path

# from dependencies_checker import DagReporting
# from generator import DevOpsHandler, DDLGenerator, DDLPublisher
# from pd_extractor import PDDocument
from logtools import get_logger, issue_tracker

from genesis import ConfigFile

logger = get_logger(__name__)


def extract(file_pd_ldm: Path, dir_output: Path) -> str:
    logger.info(f"Start extraction for '{file_pd_ldm}'")
    # document = PDDocument(file_pd_ldm=file_pd_ldm)
    file_RETW = os.path.join(dir_output, f"{file_pd_ldm.stem}.json")
    # document.write_result(file_output=file_RETW)
    logger.info(
        f"Het logisch data model en mappings van '{file_pd_ldm}' geëxtraheerd en geschreven naar '{file_RETW}'"
    )
    return file_RETW


def check_dependencies(files_RETW: list, dir_output: str) -> None:
    # dag = DagReporting()
    # dag.add_RETW_files(files_RETW=lst_files_RETW)
    pass


if __name__ == "__main__":
    lst_files_RETW = []
    file_config = Path("genesis/config.yml")
    logger.info(f"Gestart met configuratie uit '{file_config}'")
    config_file = ConfigFile(file_config=file_config)

    dir_output = config_file.dir_RETW_output
    for pd_file in config_file.pd_files:
        file_RETW = extract(file_pd_ldm=pd_file, dir_output=config_file.dir_RETW_output)
        lst_files_RETW.append(file_RETW)
    check_dependencies(
        files_RETW=lst_files_RETW, dir_output=config_file.dir_RETW_output
    )

    if issue_tracker.has_issues():
        print("Problemen gevonden:", issue_tracker.get_issues())
        file_issues = os.path.join(config_file.dir_RETW_output, "RETW_issues.csv")
        issue_tracker.write_csv(file_csv="problemen.csv")
        sys.exit("Proces gestopt nadat er issues zijn aangetroffen ")
