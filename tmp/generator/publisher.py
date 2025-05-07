import xmltodict
import codecs
import yaml
import json
from pathlib import Path

from log_config import logging

logger = logging.getLogger(__name__)

class DDLPublisher:
    """Publish SQL files in VS Studio project and add them to the SQLProject file"""

    def __init__(self, project_file: Path, file_created_ddls: Path):
        self.project_file = project_file
        self.file_created_ddls = file_created_ddls

    def publish(self):
        logger.info("--> Starting MDDE Publisher <--")
        # TODO:
        """
        Onderstaande code levert volgende foute code op:

            <PropertyGroup>
                <VisualStudioVersion Condition="'$(VisualStudioVersion)' == ''">11.0</VisualStudioVersion>
                <VisualStudioVersion Condition="'$(SSDTExists)' == ''">11.0</VisualStudioVersion>
                <SSDTExists Condition="Exists('$(MSBuildExtensionsPath)\Microsoft\VisualStudio\v$(VisualStudioVersion)\SSDT\Microsoft.Data.Tools.Schema.SqlTasks.targets')">True</SSDTExists>
            </PropertyGroup>


        Maar als wij dit handmatig nu aanpassen naar het volgende werkt hij goed. Dus uitzoeken hoe wij deze volgorde kunnen aanpassen!!

            <PropertyGroup>
                <VisualStudioVersion Condition="'$(VisualStudioVersion)' == ''">11.0</VisualStudioVersion>
                <SSDTExists Condition="Exists('$(MSBuildExtensionsPath)\Microsoft\VisualStudio\v$(VisualStudioVersion)\SSDT\Microsoft.Data.Tools.Schema.SqlTasks.targets')">True</SSDTExists>
                <VisualStudioVersion Condition="'$(SSDTExists)' == ''">11.0</VisualStudioVersion>
            </PropertyGroup>

        """
        # TODO:
        """
        we kunnen op 2 manieren nieuwe SQL bestanden toevoegen aan de XML/DICT.
        1. Door een scan te maken van de folders in de root en de bestanden en dan deze toe voegen aan de XML/DICT
        2. Door alles wat wij genereren, in lijsten bij te houden en dan deze lijsten toevogen aan deze XML/DICT.

        Dit bespreken in de refinement.

        """
        # Opening JSON file
        with open(self.file_created_ddls) as json_file:
            created_ddls = json.load(json_file)

        xml = codecs.open(self.project_file, "r", "utf-8-sig")
        org_xml = xml.read()
        dict_xml = xmltodict.parse(org_xml, process_namespaces=False)
        xml.close()
        # Remove <VisualStudioVersion Condition="'$(SSDTExists)' == ''">11.0</VisualStudioVersion> due to error in loading project in VS
        for PropertyGroup in dict_xml["Project"]["PropertyGroup"]:
            if "VisualStudioVersion" in PropertyGroup:
                for VisualStudioVersion in PropertyGroup["VisualStudioVersion"]:
                    # TODO: After initial run, wrong line is removed, but than type changes to string.. Code review to check if best solution.
                    if not isinstance(VisualStudioVersion, str):
                        if "SSDTExists" in VisualStudioVersion["@Condition"]:
                            PropertyGroup["VisualStudioVersion"].remove(
                                VisualStudioVersion
                            )
                            break

        # Add new Folders:
        for ItemGroup in dict_xml["Project"]["ItemGroup"]:
            if "Folder" in ItemGroup:
                lst_existingFolders = []
                for include in ItemGroup["Folder"]:
                    lst_existingFolders.append(include["@Include"])
                # create a list with items not already in the vs project file
                lst_addFolders = set(created_ddls["Folder Include"]) - set(
                    lst_existingFolders
                )
                for i in lst_addFolders:
                    ItemGroup["Folder"].append({"@Include": i})
                    logger.info(f"Added folder to VS SQL Project file:  {i}")

        # Add new Files:
        for ItemGroup in dict_xml["Project"]["ItemGroup"]:
            if "Build" in ItemGroup:
                lst_existingFiles = []
                for include in ItemGroup["Build"]:
                    lst_existingFiles.append(include["@Include"])
                # create a list with items not already in the vs project file
                lst_addFiles = set(created_ddls["Build Include"]) - set(
                    lst_existingFiles
                )
                for i in lst_addFiles:
                    ItemGroup["Build"].append({"@Include": i})
                    logger.info(f"Added file to VS SQL Project file:  {i}")

        # Add new Post Deploy Scripts:
        for ItemGroup in dict_xml["Project"]["ItemGroup"]:
            if "None" in ItemGroup and "Build" in ItemGroup:
                lst_existingDeployScripts = []
                for include in ItemGroup["None"]:
                    lst_existingDeployScripts.append(include["@Include"])
                # create a list with items not already in the vs project file
                lst_addDeployScripts = set(created_ddls["None Include"]) - set(
                    lst_existingDeployScripts
                )
                for i in lst_addDeployScripts:
                    ItemGroup["None"].append(
                        {"@Include": i, "CopyToOutputDirectory": "PreserveNewest"}
                    )
                    logger.info(
                        f"Added Post Deploy Scripts to VS SQL Project file:  {i}"
                    )

        out = xmltodict.unparse(dict_xml, pretty=True, short_empty_elements=False)
        with open(self.project_file, "wb") as file:
            file.write(out.encode("utf-8"))

# Run Current Class
if __name__ == "__main__":
    file_config = Path("./etl_templates/config.yml")
    if file_config.exists():
        with open(file_config) as f:
            config = yaml.safe_load(f)
    # Get params from config.yml
    file_created_ddls = Path(config["created_ddls_json"])
    project_file = Path(config["vs_project_file"])
    publisher = DDLPublisher(project_file, file_created_ddls)
    publisher.publish()
    print("Done")
