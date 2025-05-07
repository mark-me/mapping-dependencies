import json
from pathlib import Path

import sqlfluff
import sqlparse
import yaml
from jinja2 import Environment, FileSystemLoader

from log_config import logging

logger = logging.getLogger(__name__)


class DDLGenerator:
    """Class DDLGenerator genereert DDL en ETL vanuit de door RETW gemaakte Json."""

    def __init__(self, params: dict):
        """Initialiseren van de Class DDLGenerator. Hiervoor wordt de config.yml uitgelezen om parameters 
        mee te kunnen geven. Ook wordt de flow georkestreerd waarmee het Json-bestand uitgelezen wordt
        en omgezet kan worden naar DDL en ETL bestanden
        
        Args:
            params (dict): Bevat alle parameters vanuit config.yml
        """
        logger.info("Initializing Class: 'DDLGenerator'.")
        lst_params = [
            "InputFile",
            "OutputFile",
            "TemplateFolder",
            "TemplatePlatform",
            "MDDEFolder",
            "ProjectFolder",
            "ProjectFile",
            "CodeList",
        ]
        if set(params.keys()) != set(lst_params):
            logger.warning("Input params for 'DevOpsHandler' not correct.")
        self.params = params
        self.TemplateFolder = Path(
            self.params["TemplateFolder"] + self.params["TemplatePlatform"]
        )
        self.MDDEFolder = Path(
            str(self.params["MDDEFolder"]) + self.params["TemplatePlatform"]
        )

        # Create dict with lists of objects created
        self.dict_created_ddls = {}
        self.dict_created_ddls["Folder Include"] = []
        self.dict_created_ddls["Build Include"] = []
        self.dict_created_ddls["None Include"] = []

    def read_model_file(self) -> dict:
        """Leest het in  de config opgegeven Json-bestand in en slaat de informatie op in een dictionary

        Returns:
            dict_models (dict): De JSON (RETW Output) geconverteerd naar een dictionary
        """
        p = Path(self.params["InputFile"]).resolve()
        logger.info(f"Filepath MDDE Json file: {p}")
        # Function not yet used, but candidate for reading XML file
        with open(self.params["InputFile"]) as json_file:
            dict_model = json.load(json_file)
        return dict_model

    def get_templates(self) -> dict:
        """
        Haal alle templates op uit de template folder. De locatie van deze folder is opgeslagen in de config.yml

        Return:
            dict_templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """
        # Loading templates
        environment = Environment(
            loader=FileSystemLoader(self.TemplateFolder),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        dict_templates = {
            "schema": environment.get_template("create_schema.sql"),
            "Tables": environment.get_template("create_table.sql"),
            "Entities": environment.get_template("create_entity.sql"),
            "Views": environment.get_template("create_view.sql"),
            "Procedures": environment.get_template("create_procedure.sql"),
            "SourceViews": environment.get_template("create_source_view.sql"),
            "SourceViewsaggr": environment.get_template("create_source_view_agg.sql"),
            "PostDeploy_Config": environment.get_template(
                "Create MDDE_PostDeployScript_Config.sql"
            ),
            "PostDeploy_CodeList": environment.get_template(
                "Create MDDE_PostDeployScript_CodeList.sql"
            ),
        }
        return dict_templates

    def write_ddl(self, model: dict, templates: dict):
        """
        Overkoepelende functie waarin alle functions worden gestart om de diverse objecttypes op te bouwen

        Args:
            models (dict): De JSON (RETW Output) geconverteerd naar een dictionary
            templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """
        self.__copy_mdde_scripts()
        identifiers = self.__select_identifiers(model)
        self.__write_ddl_entity(model, identifiers, templates)
        self.__write_ddl_sourceview_aggr(model,templates)
        self.__write_ddl_sourceview(model, identifiers, templates)
        self.__write_ddl_MDDE_PostDeploy_Config(model, templates)
        self.__write_ddl_MDDE_PostDeploy_CodeTable(templates)

    def __copy_mdde_scripts(self):
        """
        Kopieer de MDDE scripts naar een Visual Studio Project repository folder
        """
        logger.info("Start copy of MDDE scripts to vs Project repo folder.")
        dir_output = (
            str(self.params["ProjectFolder"]) + "\\" + "CentralLayer" + "\\" + "DA_MDDE"
        )
        for platform in self.params["MDDEFolder"].iterdir():
            if platform.is_dir():
                logger.info(f"Found folder: {self.params['MDDEFolder']}\{platform.name}.")
                for schema in platform.iterdir():
                    if schema.is_dir():
                        logger.info(
                            f"Found folder: {self.params['MDDEFolder']}\{platform.name}\{schema.name}."
                        )
                        for types in schema.iterdir():
                            if types.is_dir():
                                logger.info(
                                    f"Found folder: {self.params['MDDEFolder']}\{platform.name}\{schema.name}\{types.name}."
                                )
                            for file in types.iterdir():
                                if file.is_file():
                                    # Add used folders to dict_created_ddls to be later used to add to the VS Project file
                                    if (
                                        schema.name
                                        not in self.dict_created_ddls["Folder Include"]
                                    ):
                                        self.dict_created_ddls["Folder Include"].append(
                                            schema.name
                                        )
                                    if (
                                        schema.name + "\\" + types.name
                                        not in self.dict_created_ddls["Folder Include"]
                                    ):
                                        self.dict_created_ddls["Folder Include"].append(
                                            schema.name + "\\" + types.name
                                        )
                                    if (
                                        schema.name + "\\" + types.name + "\\" + file.name
                                        not in self.dict_created_ddls["Build Include"]
                                    ):
                                        self.dict_created_ddls["Build Include"].append(
                                            schema.name + "\\" + types.name + "\\" + file.name
                                        )
                                    dir_output_type = dir_output + "/" + types.name + "/"
                                    Path(dir_output_type).mkdir(parents=True, exist_ok=True)
                                    dest = Path(dir_output_type + file.name)
                                    logger.info(f"Copy {file} to: {dest.resolve()}")
                                    dest.write_text(file.read_text())
                                    
    def __select_identifiers(self, models: dict):
        """
        Haalt alle identifiers op uit het model ten behoeve van de aanmaken van BKeys in de entiteiten en DDL's
        
        Args:
            models (dict): de JSON (RETW Output) geconverteerd naar een dictionary
        Returns:
            identifiers (dict): een dictionary met daarin alle informatie van de identifier benodigd voor het aanmaken van BKeys
        """
        #TODO: in __select_identifiers zit nu opbouw van strings die platform specifiek zijn (SSMS). Om de generator ook platform onafhankelijk te maken kijken of we dit wellicht in een template kunnen gieten.
        if "Mappings" in models:
            identifiers = {}
            strings = {}
            for mapping in models["Mappings"]:
                if "Identifiers" in mapping["EntityTarget"]:
                    if "Identifiers" in mapping["EntityTarget"]:
                        for identifier in mapping["EntityTarget"]["Identifiers"]:
                            id_entity_identifier = identifier["EntityID"]
                            attribute_identifier = identifier["Name"]
                            if "AttributeMapping" not in mapping:
                                logger.error(f"Geen attribute mapping aanwezig voor entity {mapping['EntityTarget']['Name']}")     
                            if "AttributeMapping" in mapping:
                                for attributemapping in mapping["AttributeMapping"]:
                                    #id_mapping = attributemapping["Id"]
                                    id_attribute_target =  attributemapping["AttributeTarget"]["IdEntity"]
                                    attribute_target = attributemapping["AttributeTarget"]["Code"]
                                    #selecteer alleen het attribuut uit AttributeTarget die is aangemerkt als identifier
                                    # TODO: Aangepaste filter, omdat deze issue gaf bij de regels 213+214 in de opbouw, doordat de Key niet bestond.
                                    # if id_attribute_target == id_entity_identifier and attribute_target == attribute_identifier:
                                    if id_attribute_target == id_entity_identifier:
                                        if "AttributesSource" in attributemapping:
                                            #Als het een primary key is dan nemen we als naamgeving van de BKey de code van de Entity over en zetten hier de postfix BKey achter
                                            if identifier["IsPrimary"] == True:
                                                identifier_string_entity =  "[" + identifier["EntityCode"] + "BKey] nvarchar(200) NOT NULL"
                                                identifier_string = "[" + identifier["EntityCode"] +  "BKey] =  '" + mapping["DataSource"] + "'+ '-' + CAST(" + attributemapping["AttributesSource"]["IdEntity"] +  ".[" + attributemapping["AttributesSource"]["Code"] + "] AS NVARCHAR(50))"
                                            #Is de identifier geen primary key, dan nemen we als naamgeving van de BKey de code van de AttributeTarget over en zetten hier de postfix Bkey achter
                                            else:
                                                identifier_string_entity = "[" + identifier["Code"] + "BKey] nvarchar(200) NOT NULL"
                                                identifier_string = attribute_target +  "BKey =  '" + mapping["DataSource"] + "'+ '-' + CAST(" + attributemapping["AttributesSource"]["IdEntity"] +  ".[" + attributemapping["AttributesSource"]["Code"] + "] AS NVARCHAR(50))"
                                        #Als er geen AttributeSource beschikbaar is in AttributeMapping hebben we de maken met een expression. De Bkey wordt hiervoor anders opgebouwd                                          
                                        else:
                                            #Als het een primary key is dan nemen we als naamgeving van de BKey de code van de Entity over en zetten hier de postfix  BKey achter
                                            if identifier["IsPrimary"] == True:
                                                identifier_string_entity =  "[" + identifier["EntityCode"] + "BKey] nvarchar(200) NOT NULL"
                                                identifier_string = "[" + identifier["EntityCode"] +  "BKey] = '" + mapping["DataSource"] +  "'+  '-' +  " + attributemapping["Expression"]
                                            #Is de identifier geen primary key, dan nemen we als naamgeving van de BKey de code van de AttributeTarget over en zetten hier de postfix BKey achter
                                            else:
                                                identifier_string_entity = "[" + identifier["Code"] + "BKey] nvarchar(200) NOT NULL"
                                                identifier_string = "[" + attribute_target +  "BKey] = '" + mapping["DataSource"] +  "'+  '-' +  " + attributemapping["Expression"]
                                        strings[identifier["Id"]] = {
                                            "IdentifierId": identifier["Id"],
                                            "IdentifierStringEntity": identifier_string_entity,
                                            "IdentifierStringSourceview": identifier_string,    
                                            }               
                            identifier_string_entity = strings[identifier["Id"]]["IdentifierStringEntity"]
                            identifier_string = strings[identifier["Id"]]["IdentifierStringSourceview"]
                            identifiers[identifier["Id"]] = {
                                "IdentifierID": identifier["Id"],
                                "IdentifierName": identifier["Name"],
                                "IdentifierCode": identifier["Code"],
                                "EntityId": identifier["EntityID"],
                                "EntityCode": identifier["EntityCode"],
                                "IsPrimary": identifier["IsPrimary"],
                                "IdentifierStringEntity": identifier_string_entity,
                                "IdentifierStringSourceView": identifier_string,
                            } 
                    else:
                        logger.error(f"Geen identifiers aanwezig voor entitytarget {mapping['EntityTarget']['Name']}")            
            else:
                pass
        return identifiers
        
    def __write_ddl_entity(self, models: dict, identifiers: dict, templates: dict):
        """
        Creëert alle DDL's van de verschillende entiteiten die in models zijn opgenomen en schrijft deze weg naar een folder in de repository

        Args:
            models (dict): De JSON (RETW Output) geconverteerd naar een dictionary
            templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """
        for model in models["Models"]:
            if model["IsDocumentModel"]:
                for entity in model["Entities"]:
                    # TODO: Entity always needs attribute number. This is used for distribution
                    if "Number" not in entity:
                        entity["Number"] = 0
                    # TODO: Add filter out filter in entity
                    # TODO: Add CodeModel to Json and not here
                    entity["CodeModel"] = model["Code"]
                    dir_output = (
                        str(self.params["ProjectFolder"])
                        + "\\"
                        + "CentralLayer"
                        + "\\"
                        + model["Code"]
                    )
                    dir_output_type = dir_output + "/" + "Tables" + "/"
                    file_output = entity["Code"] + ".sql"

                    # Add used folders to dict_created_ddls to be later used to add to the VS Project file
                    if (
                        model["Code"]
                        not in self.dict_created_ddls["Folder Include"]
                    ):
                        self.dict_created_ddls["Folder Include"].append(
                            model["Code"]
                        )
                    if (
                        model["Code"] + "\Tables"
                        not in self.dict_created_ddls["Folder Include"]
                    ):
                        self.dict_created_ddls["Folder Include"].append(
                            model["Code"] + "\Tables"
                        )
                    if (
                        model["Code"] + "\Tables\\" + file_output
                        not in self.dict_created_ddls["Build Include"]
                    ):
                        self.dict_created_ddls["Build Include"].append(
                            model["Code"] + "\Tables\\" + file_output
                        )

                    # Fill Path with the destination directory. Path is used for file system operations
                    directory = Path(dir_output_type)
                    # Make directory if not exist.
                    directory.mkdir(parents=True, exist_ok=True)
                    #bouw de Bkeys op op basis van de identifiers bij de entity
                    mapped_identifiers = []
                    identifier_mapped = []
                    for identifier in entity["Identifiers"]:
                        identifier_id = identifier["Id"]
                        if identifier_id in identifiers:
                            identifier_info = identifiers[identifier_id]["IdentifierStringEntity"]
                            identifier_mapped.append(identifier_info)
                            #voeg de code van de identifier toe aan een controlelijst. De attributen in deze lijst worden verwijderd uit entity[Attributes]
                            mapped_identifiers.append(identifiers[identifier_id]["IdentifierName"])
                        else:
                            logger.error(f"identifier voor {entity['Code']} niet gevonden in identifiers")
                    #Voeg de complete lijst van identifiers toe aan de entity
                    entity["Identifiers"] = identifier_mapped
                    attributes = []
                    #voor alle attributen in de entity gaan we controleren of de code voorkomt als gemapte identifier. Indien dit het geval is, dan wordt het
                    #attribuut verwijderd uit Attributes. Hiermee krijgen we geen dubbelingen in de entiteit.
                    for attribute in entity["Attributes"]:
                        if attribute["Code"] not in mapped_identifiers:
                            attributes.append(attribute)
                    #verwijder de oude Attributes uit entity en vervang deze met attributes (opgeschoonde lijst)
                    entity.pop("Attributes")
                    entity["Attributes"] = attributes
                    entity = entity
                    #bepaal welke template we gaan gebruiken en maak de DDL's aan voor de entity
                    content = templates["Entities"].render(entity=entity)
                    # Using 'sqlparse' library we can format the sqls.
                    # content = sqlparse.format(
                    #     content, 
                    #    # reindent=False, 
                    #     keyword_case="upper", 
                    #     strip_comments=True , 
                    #     strip_whitespace=False, 
                    #    # reindent_aligned=True, 
                    #     compact=True,
                    #     comma_first =True,
                    # ).strip()
                    # content = sqlfluff.fix(content,dialect="tsql")
                    print(content)
                    with open(
                        dir_output_type + file_output, mode="w", encoding="utf-8"
                    ) as file_ddl:
                        file_ddl.write(content)
                    logger.info(
                        f"Written Entity DDL {Path(dir_output_type + file_output).resolve()}"
                    )
                    # p = Path(self.file_input).resolve()
                    
    def __write_ddl_sourceview_aggr(self, models: dict, templates:dict):
        """
        Creëert alle sourceviews van de verschillende aggregatie entiteiten die in models zijn opgenomen en schrijft deze weg naar een folder in de repository. 
        De sourceviews bevatten de ETL om de doeltabel te vullen met data.

        Args:
            models (dict): De JSON (RETW Output) geconverteerd naar een dictionary
            templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """        
        if  "Mappings" in models:
            for mapping in models["Mappings"]:
                if mapping["EntityTarget"]["Stereotype"] == 'mdde_AggregateBusinessRule':
                    dir_output = (
                        str(self.params["ProjectFolder"])
                        + "\\"
                        + "CentralLayer"
                        + "\\"
                        + mapping["EntityTarget"]["CodeModel"]
                    )
                    dir_output_type = dir_output + "/" + "Views" + "/"  
                    file_output = "vw_src_" + mapping['EntityTarget']['Code'] + "_" + mapping['DataSource'] + ".sql"   
                    if (
                        mapping["EntityTarget"]["CodeModel"]
                        not in self.dict_created_ddls["Folder Include"]
                    ):
                        self.dict_created_ddls["Folder Include"].append(
                            mapping["EntityTarget"]["CodeModel"]
                        )
                    if (
                        mapping["EntityTarget"]["CodeModel"] + "\Views"
                        not in self.dict_created_ddls["Folder Include"]
                    ):
                        self.dict_created_ddls["Folder Include"].append(
                            mapping["EntityTarget"]["CodeModel"] + "\Views"
                        )
                    if (
                        mapping["EntityTarget"]["CodeModel"] + "\Views\\" + file_output
                        not in self.dict_created_ddls["Build Include"]
                    ):
                        self.dict_created_ddls["Build Include"].append(
                            mapping["EntityTarget"]["CodeModel"] + "\Views\\" + file_output
                        )

                    # Fill Path with the destination directory. Path is used for file system operations
                    directory = Path(dir_output_type)
                    # Make directory if not exist.
                    directory.mkdir(parents=True, exist_ok=True)  
                    
                    if "DataSource" in mapping:
                        datasource = mapping["DataSource"]  
                        if datasource[0:3] == "SL_":
                            datasourcecode = datasource[3:]
                            mapping["DataSourceCode"] = datasourcecode
                        else:
                            mapping["DataSourceCode"] = datasource
                    else:
                        logger.warning(f"Geen datasource opgegeven voor mapping {mapping['Name']}")        
                    content = templates['SourceViewsaggr'].render(mapping=mapping)
                    # Using 'sqlparse' library we can format the sqls.
                    content = sqlparse.format(
                        content, reindent=True, keyword_case="upper"
                    )
                    with open(
                        dir_output_type + file_output, mode="w", encoding="utf-8"
                    ) as file_ddl:
                        file_ddl.write(content)
                    logger.info(
                        f"Written Source view DDL {Path(dir_output_type + file_output).resolve()}"
                    )
        
    def __write_ddl_sourceview(self, models: dict, identifiers: dict, templates: dict):
        """
        Creëert alle sourceviews van de verschillende niet-aggregatie entiteiten die in models zijn opgenomen en schrijft deze weg naar een folder in de repository. 
        De sourceviews bevatten de ETL om de doeltabel te vullen met data.

        Args:
            models (dict): De JSON (RETW Output) geconverteerd naar een dictionary
            templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """    
        # Fix old layout into v2 layout
        if "Transformations" in models:
            if "Mappings" in models["Transformations"]:
                if "Mappings" not in models:
                    models["Mappings"] = models["Transformations"]["Mappings"]
        if "Mappings" in models:
            for mapping in models["Mappings"]:
                if mapping["EntityTarget"]["Stereotype"] != 'mdde_AggregateBusinessRule':
                    dir_output = (
                        str(self.params["ProjectFolder"])
                        + "\\"
                        + "CentralLayer"
                        + "\\"
                        + mapping["EntityTarget"]["CodeModel"]
                    )
                    dir_output_type = dir_output + "/" + "Views" + "/"

                    file_output = "vw_src_" + mapping['EntityTarget']['Code'] + "_" + mapping['DataSource'] + ".sql"

                    # Add used folders to dict_created_ddls to be later used to add to the VS Project file
                    if (
                        mapping["EntityTarget"]["CodeModel"]
                        not in self.dict_created_ddls["Folder Include"]
                    ):
                        self.dict_created_ddls["Folder Include"].append(
                            mapping["EntityTarget"]["CodeModel"]
                        )
                    if (
                        mapping["EntityTarget"]["CodeModel"] + "\Views"
                        not in self.dict_created_ddls["Folder Include"]
                    ):
                        self.dict_created_ddls["Folder Include"].append(
                            mapping["EntityTarget"]["CodeModel"] + "\Views"
                        )
                    if (
                        mapping["EntityTarget"]["CodeModel"] + "\Views\\" + file_output
                        not in self.dict_created_ddls["Build Include"]
                    ):
                        self.dict_created_ddls["Build Include"].append(
                            mapping["EntityTarget"]["CodeModel"] + "\Views\\" + file_output
                        )

                    # Fill Path with the destination directory. Path is used for file system operations
                    directory = Path(dir_output_type)
                    # Make directory if not exist.
                    directory.mkdir(parents=True, exist_ok=True)
                    
                    if "DataSource" in mapping:
                        datasource = mapping["DataSource"]  
                        if datasource[0:3] == "SL_":
                            datasourcecode = datasource[3:]
                            mapping["DataSourceCode"] = datasourcecode
                        else:
                            mapping["DataSourceCode"] = datasource
                    else:
                        logger.warning(f"Geen datasource opgegeven voor mapping {mapping['Name']}")    
                    
                    #bouw de string voor de BKey op en geef deze mee aan de render voor de SourceView
                    mapped_identifiers = []
                    identifier_mapped = []
                    for identifier in mapping["EntityTarget"]["Identifiers"]:
                        identifier_id = identifier["Id"]
                        if identifier_id in identifiers:
                            identifier_info = identifiers[identifier_id]["IdentifierStringSourceView"]
                            identifier_mapped.append(identifier_info)
                            #voeg de code van de identifier toe aan een controlelijst. De attributen in deze lijst worden verwijderd uit entity[Attributes]
                            mapped_identifiers.append(identifiers[identifier_id]["IdentifierName"])
                        else:
                            logger.error(f"identifier voor {mapping['EntityTarget']['Code']} niet gevonden in identifiers")
                    #Voeg de complete lijst van identifiers toe aan de entity
                    mapping["Identifiers"] = identifier_mapped
                    #De identifiers die zijn toegevoegd aan PrimaryKeys willen we niet meer in de mapping toevoegen. Omdat deze velden nog wel meegaan in de x_hashkey bouwen we tegelijkertijd dit attribuut op. Doen we dit niet, dan hebben we een incomplete hashkey in de template 
                    attributemappings = []
                    #TODO: afhandeling van x_hashkey bevat platform specifieke logica (in dit geval SSMS). Dit platform onafhankelijk maken door het bijvoorbeeld te gieten in een string_template
                    #string van x_hashkey in basis. Hieraan voegen wij de hashattributen toe in de for loop die volgt
                    x_hashkey = "[X_HashKey] = HASHBYTES('SHA2_256', CONCAT("
                    #teller om de seperator (,) mee te geven aan de x_hashkey string die we opbouwen.
                    x_hashkey_teller = 0
                    for attributemapping in mapping["AttributeMapping"]:
                        #eerste ronde van de for-loop, dan seperator leeg, anders komma (,)
                        if x_hashkey_teller == 0:
                            seperator = ''
                        else:
                            seperator = ','
                        if  'Expression' in attributemapping:
                            hash_attrib = seperator + "DA_MDDE.fn_IsNull(" + attributemapping["Expression"] + ")" 
                            x_hashkey = x_hashkey + hash_attrib
                            x_hashkey_teller += 1
                        else:
                            hash_attrib = seperator + "DA_MDDE.fn_IsNull(" + attributemapping["AttributesSource"]["IdEntity"] +  ".["  + attributemapping["AttributesSource"]["Code"] + "])" 
                            x_hashkey = x_hashkey + hash_attrib
                            x_hashkey_teller +=1
                        #we nemen alleen de non-identifier velden mee naar de attributemapping die de template ingaat.
                        if attributemapping["AttributeTarget"]["Code"] not in mapped_identifiers:
                            attributemappings.append(attributemapping)
                        else:
                            pass
                    #verwijder uit mapping het gedeelte van AttributeMapping. Deze voegen we opnieuw toe met de zojuist aangemaakte attributemappings
                    mapping.pop("AttributeMapping")
                    mapping["AttributeMapping"] = attributemappings
                    #voeg de x_hashkey als kenmerk toe aan de mapping
                    mapping["X_Hashkey"] = x_hashkey + ",'" + mapping["DataSource"] + "'))"
                    #bepaal welke template we gaan gebruiken
                    content = templates['SourceViews'].render(mapping=mapping) 
                    # Using 'sqlparse' library we can format the sqls.
                    content = sqlparse.format(
                        content, reindent=True, keyword_case="upper"
                    )
                    with open(
                        dir_output_type + file_output, mode="w", encoding="utf-8"
                    ) as file_ddl:
                        file_ddl.write(content)
                    logger.info(
                        f"Written Source view DDL {Path(dir_output_type + file_output).resolve()}"
                    )

    def __write_ddl_MDDE_PostDeploy_Config(self, models: dict, templates: dict):
        """
        Creëert het post deploy script voor alle mappings opgenomen in het model. Voor elke mapping wordt een insert statement aangemaakt
        waarmee een record aangemaakt wordt in de tabel [DA_MDDE].[Config]. 
        Voor elk model wordt een eigen post deployment bestand aangemaakt. Deze worden vervolgens uitgevoerd door 1 master file samen met
        andere post deployment activiteiten

        Args:
            models (dict): De JSON (RETW Output) geconverteerd naar een dictionary
            templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """
        for model in models["Models"]:
            if model["IsDocumentModel"]:
                name_model = model["Name"].replace(" ", "_")
        if "Mappings" in model:
            dir_output = str(self.params["ProjectFolder"]) + "\\" + "CentralLayer" + "\\" + "DA_MDDE"
            dir_output_type = dir_output + "/" + "PostDeployment" + "/"
            file_output = f"PostDeploy_MetaData_Config_{name_model}.sql"
            file_output_master = "PostDeploy_MetaData.sql"
            file_output_master_full = Path(str(self.params["ProjectFolder"]) + "/" + "CentralLayer" + "/" + "PostDeployment" + "/" + file_output_master)
            

            # Add used folders to self.dict_created_ddls to be later used to add to the VS Project file
            if "DA_MDDE" not in self.dict_created_ddls["Folder Include"]:
                self.dict_created_ddls["Folder Include"].append("DA_MDDE")
            if "DA_MDDE" + "\PostDeployment" not in self.dict_created_ddls["Folder Include"]:
                self.dict_created_ddls["Folder Include"].append(
                    "DA_MDDE" + "\PostDeployment"
                )
            if (
                "DA_MDDE" + "\PostDeployment\\" + file_output
                not in self.dict_created_ddls["None Include"]
            ):
                self.dict_created_ddls["None Include"].append(
                    "DA_MDDE" + "\PostDeployment\\" + file_output
                )
            if (
                "\PostDeployment\\" + file_output_master
                not in self.dict_created_ddls["None Include"]
            ):
                self.dict_created_ddls["None Include"].append(
                "\PostDeployment\\" + file_output_master
                )

            # Fill Path with the destination directory. Path is used for file system operations
            directory = Path(dir_output_type)
            # Make directory if not exist.
            directory.mkdir(parents=True, exist_ok=True)
            content = templates["PostDeploy_Config"].render(config=models)
            with open(
                dir_output_type + file_output, mode="w", encoding="utf-8"
            ) as file_ddl:
                file_ddl.write(content)
            logger.info(
                f"Written MDDE PostDeploy_Config file {Path(dir_output_type + file_output).resolve()}"
            )

            # Add file to master file.
            if not file_output_master_full.is_file():
                f = open(file_output_master_full, "a")
                f.write("/* Post deploy master file. */\n")
                f.close()
            if file_output_master_full.is_file():
                fr = open(file_output_master_full, "r")
                if f":r ..\DA_MDDE\PostDeployment\{file_output}\n" not in fr.read():
                    fr.close()
                    f = open(file_output_master_full, "a")
                    f.write(f"\nPRINT N'Running PostDeploy: ..\DA_MDDE\PostDeployment\{file_output}\n")
                    f.write(f":r ..\DA_MDDE\PostDeployment\{file_output}\n")
                    f.close()

    def __write_ddl_MDDE_PostDeploy_CodeTable(self, templates: dict):
        """
        Creëert het post deploy script voor de CodeTable. Voor elk record in de CodeList wordt een select
        statement gemaakt waarmee de data geladen kan worden in [DA_MDDE].[CodeList]

        Args:
            templates (dict): Bevat alle beschikbare templates en de locatie waar de templates te vinden zijn
        """
        # Opening JSON file
        with open(self.params["CodeList"]) as json_file:
            codeList = json.load(json_file)

        if self.params["CodeListFolder"].exists():
            dir_output = str(self.params["ProjectFolder"]) + "/" + "CentralLayer" + "/" + "DA_MDDE"
            dir_output_type = dir_output + "/" + "PostDeployment" + "/"
            file_output = "PostDeploy_MetaData_Config_CodeList.sql"
            file_output_full = Path(dir_output_type + file_output)
            file_output_master = "PostDeploy.sql"
            file_output_master_full = Path(str(self.params["ProjectFolder"]) + "/" + "CentralLayer" + "/" +  "PostDeployment" + "/" + file_output_master)


            # Add used folders to dict_created_ddls to be later used to add to the VS Project file
            if "DA_MDDE" not in self.dict_created_ddls["Folder Include"]:
                self.dict_created_ddls["Folder Include"].append("DA_MDDE")
            if "DA_MDDE" + "\PostDeployment" not in self.dict_created_ddls["Folder Include"]:
                self.dict_created_ddls["Folder Include"].append(
                    "DA_MDDE" + "\PostDeployment"                )
            if (
                "DA_MDDE" + "\PostDeployment\\" + file_output
                not in self.dict_created_ddls["None Include"]
            ):
                self.dict_created_ddls["None Include"].append(
                    "DA_MDDE" + "\PostDeployment\\" + file_output
                )
            if (
                "\PostDeployment\\" + file_output_master
                not in self.dict_created_ddls["None Include"]
            ):
                self.dict_created_ddls["None Include"].append(
                    "\PostDeployment\\" + file_output_master
                )

            content = templates["PostDeploy_CodeList"].render(codeList=codeList)

            Path(dir_output_type ).mkdir(parents=True, exist_ok=True)
            with open(file_output_full, mode="w", encoding="utf-8") as file_ddl:
                file_ddl.write(content)
            logger.info(
                f"Written CodeTable Post deploy script: {file_output_full.resolve()}"
            )

            # Add file to master file.
            if not file_output_master_full.is_file():
                f = open(file_output_master_full, "a")
                f.write("/* Post deploy master file. */\n")
                f.close()
            if file_output_master_full.is_file():
                fr = open(file_output_master_full, "r")
                if f":r ..\DA_MDDE\PostDeployment\{file_output}\n" not in fr.read():
                    fr.close()
                    f = open(file_output_master_full, "a")
                    f.write(f"\nPRINT N'Running PostDeploy: ..\DA_MDDE\PostDeployment\{file_output}\n")
                    f.write(f":r ..\DA_MDDE\PostDeployment\{file_output}\n")
                    f.close()

    def write_json_created_ddls(self):
        """
        Creëert een Json file met daarin alle DDL's en ETL's die zijn gemaakt vanuit het model. Dit JSON-bestand
        is input voor de Publisher
        """
        with open(self.params["OutputFile"], mode="w", encoding="utf-8") as file_ddl:
            json.dump(self.dict_created_ddls, file_ddl, indent=4)
        logger.info(
            f"""Written dict_created_ddls to JSON file: {Path(self.params["OutputFile"]).resolve()}"""
        )

# Run Current Class
if __name__ == "__main__":
    file_config = Path("./etl_templates/config.yml")
    if file_config.exists():
        with open(file_config) as f:
            config = yaml.safe_load(f)
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
    ddl_generator = DDLGenerator(generatorParams)
    model = ddl_generator.read_model_file()
    templates = ddl_generator.get_templates()
    ddl_generator.write_ddl(model, templates)
    ddl_generator.write_json_created_ddls()
    print("Done")
