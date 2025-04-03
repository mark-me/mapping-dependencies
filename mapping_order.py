import json

import pandas as pd

from log_config import logging

logger = logging.getLogger(__name__)


class MappingDependencyParser:
    def __init__(self):
        self.mappings = []
        self.df_nodes = pd.DataFrame()
        self.df_links = pd.DataFrame()

    def load_RETW_file(self, file: str) -> bool:
        """Load a RETW json file

        Args:
            file (str): RETW file containing mappings

        Returns:
            bool: Indicates whether the RETW file was processed
        """
        try:
            with open(file_RETW) as file:
                dict_RETW = json.load(file)
        except FileNotFoundError:
            logger.error(f"Could not find file '{file}'")
            return False

        if "Mappings" in dict_RETW:
            lst_mappings = dict_RETW["Mappings"]
            self.mappings.append(lst_mappings)
            for mapping in lst_mappings:
                self._add_mapping(dict_mapping=mapping)
        else:
            logger.warning(f"Couldn't find mappings in RETW file '{file}'")

        return True

    def _add_mapping(self, dict_mapping: dict) -> bool:
        """Create nodes and edges based on mapping

        Args:
            dict_mapping (dict): RETW mapping
        """
        # Create a node from the mapping information
        keys_mapping = [
            "Id",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
        ]
        df_node = pd.DataFrame({key: dict_mapping[key] for key in keys_mapping})
        self.df_nodes = pd.concat(
            pd.concat([self.df_nodes, df_node], ignore_index=True)
        )

        # Create nodes for target and source entities
        keys_entity = [
            "Id",
            "Name",
            "Code",
            "IdModel",
            "NameModel",
            "CodeModel",
            "IsDocumentModel",
        ]
        if "EntityTarget" in dict_mapping:
            self._create_target_nodes(
                dict_mapping["EntityTarget"], entity_keys=keys_entity
            )
        else:
            logger.error(
                f"Could not find target entity for mapping '{dict_mapping['Name']}'"
            )
            return False
        if "SourceComposition" in dict_mapping:
            df_sources = self._create_source_nodes(
                dict_mapping["SourceComposition"], entity_keys=keys_entity
            )
        else:
            return False
        # dict_mapping[]
        return True

    def _create_target_nodes(self, entity_target: dict, entity_keys: list) -> pd.DataFrame:
        """_summary_

        Args:
            dict_entity_target (dict): Data on the target entity
            lst_entity_keys (list): Entity data to include in the node
        """
        df_node = pd.DataFrame({key: entity_target[key] for key in entity_keys})
        return df_node

    def _create_source_nodes(self, entity_sources: dict, entity_keys: list) -> pd.DataFrame:
        """_summary_

        Args:
            dict_entity_target (dict): _description_
            lst_entity_keys (list): _description_
        """
        for source in entity_sources:
            source_entity = source["Entity"]
            df_node = pd.DataFrame({key: source_entity[key] for key in entity_keys})
            self.df_nodes = pd.concat(
                pd.concat([self.df_nodes, df_node], ignore_index=True)
            )


if __name__ == "__main__":
    lst_files_RETW = ["etl_templates/output/Usecase_Aangifte_Behandeling.json"]
    dep_parser = MappingDependencyParser()

    for file_RETW in lst_files_RETW:
        success = dep_parser.load_RETW_file(file=file_RETW)
        if success:
            dep_parser.mappings
