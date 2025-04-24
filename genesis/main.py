import os
import sys
from pathlib import Path

#from dependencies_checker import DagReporting
#from generator import DevOpsHandler, DDLGenerator, DDLPublisher
from pd_extractor import PDDocument
from logtools import get_logger, issue_tracker

from genesis import ConfigFile

logger = get_logger(__name__)


def extraction(file_pd_ldm: Path, dir_output: Path) -> str:
    # "output/ExampleDWH.json"
    document = PDDocument(file_pd_ldm=file_pd_ldm)
    file_RETW = os.path.join(dir_output, file_pd_ldm.stem + ".json")
    # Saving model objects
    #document.write_result(file_output=file_RETW)
    logger.info(
        f"Done extracting the logical data model and mappings of '{file_pd_ldm}' written to '{file_RETW}'"
    )
    return file_RETW


if __name__ == "__main__":
    lst_files_RETW = []
    # Load config from file
    file_config = Path("./etl_templates/src/genesis/config.yml")
    config_file = ConfigFile(file_config=file_config)
    logger.info("Start extraction")
    for pd_file in config_file.pd_files:
        file_RETW = extraction(
            file_pd_ldm=pd_file, dir_output=config_file.dir_RETW_output
        )
        lst_files_RETW.append(file_RETW)

    #dag = DagReporting()
    #dag.add_RETW_files(files_RETW=lst_files_RETW)

    if issue_tracker.has_issues():
        print("Problemen gevonden:", issue_tracker.get_issues())
        file_issues = os.path.join(config_file.dir_RETW_output, "RETW_issues.csv")
        issue_tracker.write_csv(file_csv="problemen.csv")
        sys.exit("Proces gestopt nadat er issues zijn aangetroffen ")
