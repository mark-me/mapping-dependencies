import os
import time
from pathlib import Path
import shutil
import webbrowser
import yaml
from log_config import logging

from generator import DDLGenerator
from publisher import DDLPublisher

logger = logging.getLogger(__name__)


class DevOpsHandler:
    """Nog te doen
    """
    def __init__(self, params: dict):
        logger.info("Initializing Class: 'DevOpsHandler'.")
        lst_params = [
            "ProjectFolder",
            "ProjectFile",
            "Branch",
            "WorkItem",
            "WorkItemDesc",
            "Organisation",
            "Destination",
            "Project",
            "Repo",
        ]
        if set(params.keys()) != set(lst_params):
            logger.warning("Input params for 'DevOpsHandler' not correct.")
        self.params = params
        # Build config string based on params
        self.featurebranch = f"feature/{self.params['WorkItem']}_{self.params['WorkItemDesc'].replace(' ', '_')}"
        self.devOps_URL = f"https://{self.params['Organisation']}@dev.azure.com/{self.params['Organisation']}/{self.params['Project']}/_git/{self.params['Repo']}"
        self.devOps_URLCheck = f"https://dev.azure.com/{self.params['Organisation']}/{self.params['Project']}/_git/{self.params['Repo']}"
        self.devOps_branchURL = f"https://dev.azure.com/{self.params['Organisation']}/{self.params['Project']}/_git/{self.params['Repo']}?version=GBfeature%2F{self.params['WorkItem']}_{self.params['WorkItemDesc'].replace(' ', '_')}"

    def get_repo(self):
        """
        
        """
        logger.info("Initializing Function: 'devopsgetrepo'.")
        currentFolder = Path("./").resolve()
        if os.path.isdir(self.params["Destination"].resolve()):
            # change owner of file .idx, else we get an error
            for root, dirs, files in os.walk(self.params["Destination"].resolve()):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o777)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o777)
            logger.info(
                f"Delete existing folder: {self.params['Destination'].resolve()}"
            )
            shutil.rmtree(
                self.params["Destination"].resolve()
            )  # deletes a directory and all its contents.
        time.sleep(5)
        for i in range(0, 2):
            try:
                logger.info(
                    f"git clone {self.devOps_URL} -b {self.params['Branch']} {str(self.params['Destination'])}"
                )
                os.system(
                    f"git clone {self.devOps_URL} -b {self.params['Branch']} {str(self.params['Destination'])}"
                )
                logger.info(f"chdir to: {self.params['Destination'].resolve()}")
                os.chdir(self.params["Destination"].resolve())
                logger.info(f"git branch {self.featurebranch} {self.params['Branch']}")
                os.system(f"git branch {self.featurebranch} {self.params['Branch']}")
                logger.info(f"git switch {self.featurebranch}")
                os.system(f"git switch {self.featurebranch}")
                # Create all DDL and ETL Files and store them in the new repo folder
                i += 99
            except:
                print(
                    "Er is wat mis gegaan. Waarschijnlijk moet je eerst inloggen op Devops. "
                )
                webbrowser.open(self.devOps_URLCheck, new=0, autoraise=True)
                print("Wait timer for 15 seconds, to allow user to log in to DevOps")
                time.sleep(15)
                continue
            else:
                break
        # Relocate to org root folder
        os.chdir(currentFolder.resolve())

    def publish_repo(self):
        """
        
        """
        logger.info(
            f"""git add -A && git commit -m "Commit: {self.params['WorkItemDesc'].replace(' ', '_')} #{int(self.params['WorkItem'])}" """
        )
        os.chdir(self.params["Destination"].resolve())
        os.system(
            f"""git add -A && git commit -m "Commit: {self.params['WorkItemDesc'].replace(' ', '_')} #{int(self.params['WorkItem'])}" """
        )
        logger.info(f"git push origin {self.featurebranch}")
        os.system(f"git push origin {self.featurebranch}")

        # Open browser to check Commit tot DevOps
        webbrowser.open(self.devOps_branchURL, new=0, autoraise=True)


# Run Current Class
if __name__ == "__main__":
    file_config = Path("./etl_templates/config.yml")
    if file_config.exists():
        with open(file_config) as f:
            config = yaml.safe_load(f)
    # Build dict params
    devopsParams = {
        "ProjectFolder": Path(config["vs_project_folder"]),
        "ProjectFile": Path(config["vs_project_file"]),
        "Branch": config["devOps_Branch"],
        "WorkItem": config["devOps_WorkItem"],
        "WorkItemDesc": config["devOps_WorkItemDesc"],
        "Destination": Path(config["vs_project_folder"]),
        "Organisation": config["devOps_Organisation"],
        "Project": config["devOps_Project"],
        "Repo": config["devOps_Repo"],
    }
    # Init DevOpsHandler
    dev_ops_handler = DevOpsHandler(devopsParams)
    dev_ops_handler.get_repo()
    print("Starting Create_DDL Class.")
    DDLGenerator()
    print("Starting Publish_VS_Project Class. Adds the new files to the VS SQL Project.")
    DDLPublisher()
    dev_ops_handler.publish_repo()
    print("Done")
