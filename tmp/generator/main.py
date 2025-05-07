from pathlib import Path
import yaml
from log_config import logging
from generator import DDLGenerator
from publisher import DDLPublisher
from devops import DevOpsHandler
from codelists import CodeList

logger = logging.getLogger(__name__)

def main():
    # Load config from file
    file_config = Path("./etl_templates/config.yml")
    if file_config.exists():
        with open(file_config) as f:
            config = yaml.safe_load(f)

    # Get params from config
    file_created_ddls = Path(config["created_ddls_json"])
    project_file = Path(config["vs_project_file"])
    codelist = Path(config["codeList_json"])
    codelistfolder =  Path(config["codeList_folder"])

    # Build dict params
    generatorParams = {
        "InputFile": Path(config["mdde_json"]),
        "OutputFile": Path(config["created_ddls_json"]),
        "TemplateFolder": config["templates_folder"],
        "TemplatePlatform": config["templates_platform"],
        "MDDEFolder": Path(config["mdde_scripts_folder"]),
        "ProjectFolder": Path(config["vs_project_folder"]),
        "ProjectFile": Path(config["vs_project_file"]),
        "CodeList": Path(config["codeList_json"]),
        "CodeListFolder": Path(config["codeList_folder"])
     }
    devopsParams = {
        "ProjectFolder": Path(config["vs_project_folder"]),
        "ProjectFile": Path(config["vs_project_file"]),
        "Branch": config["devOps_Branch"],
        "WorkItem": config["devOps_WorkItem"],
        "WorkItemDesc": config["devOps_WorkItemDesc"],
        "Destination": Path(config["vs_project_folder"]),
        "Organisation": config["devOps_Organisation"],
        "Project": config["devOps_Project"],
        "Repo": config["devOps_Repo"]
    }

    # Initializing Classes:
    codelistmaker = CodeList(codelistfolder, codelist)
    devops_handler = DevOpsHandler(devopsParams)
    ddl_generator = DDLGenerator(generatorParams)
    publisher = DDLPublisher(project_file, file_created_ddls)
    #ddl_publisher = DDLPublisher()

    # 1. Generatate CodeList.json from input codelist files
    codelistmaker.read_CodeLists()
    codelistmaker.write_CodeLists()
    # 2. Clone a clean copy of the DevOps Repo to disk, and create a new brach based on the config params.
    devops_handler.get_repo()
    # 3. Read the model JSON file(s)
    model = ddl_generator.read_model_file()
    # 4. Read the templates and filenames of the templates
    templates = ddl_generator.get_templates()
    # 5. Write all DLL, SoureViews and MDDE ETL to the Repo
    ddl_generator.write_ddl(model, templates)
    # 6. Write a JSON that contains all list with al written objects with there type. Is used by the publisher.
    ddl_generator.write_json_created_ddls()
    # 7. Write all new created DDL and ETL file to the VS SQL Project file as a reference.
    publisher.publish()
    # 8. Commit changes to GIT/DEVOPS and sync the changes to the online repo.
    devops_handler.publish_repo()
    print("Done")

# Run Current Class
if __name__ == "__main__":
    main()
    print("Done")
