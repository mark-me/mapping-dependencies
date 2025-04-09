import json
from pathlib import Path

import igraph as ig
import networkx as nx
from pyvis.network import Network

from log_config import logging

logger = logging.getLogger(__name__)


class Graph_RETW_Files:
    def __init__(self):
        self.files = {}
        self.entities = {}
        self.mappings = {}
        self.edges = []

    def add_RETW_files(self, files_RETW: list, generate_plot: bool = False) -> bool:
        """Process multiple RETW files.

        Processes each RETW file in the input list, generates the mapping order,
        and creates a DAG visualization.
        Args:
            files_RETW (list): list of RETW file containing mappings

        Returns:
            bool: Indicates whether all RETW file were processed
        """
        # Make sure added files are unique
        self.files_RETW = list(set(files_RETW))

        # Process files
        for i, file_RETW in enumerate(self.files_RETW):
            # Add file to parser
            if self.add_RETW_file(file_RETW=file_RETW):
                logger.info(f"Added RETW file '{file_RETW}'")
            else:
                logger.error(f"Failed to add RETW file '{file_RETW}'")
                return False
        return True

    def add_RETW_file(self, file_RETW: str) -> bool:
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
            logger.error(f"Could not find file '{file_RETW}'")
            return False

        # Add file node information
        order_added = len(self.files)
        self.files.update(
            {
                file_RETW: {
                    "Order": order_added,
                    "TimeCreated": Path(file_RETW).stat().st_birthtime,
                    "TimeModified": Path(file_RETW).stat().st_mtime,
                }
            }
        )
        self._add_model_entities(file_RETW, dict_RETW=dict_RETW)
        self._add_mappings(file_RETW, mappings=dict_RETW["Mappings"])

    def _add_model_entities(self, file_RETW: str, dict_RETW: list):
        # Determine document model
        model = [model for model in dict_RETW["Models"] if model["IsDocumentModel"] == True][0]
        if "Entities" not in model:
            logger.warning(f"No entities for a document model in '{file_RETW}'")
            return

        for entity in model["Entities"]:
            dict_entity = {
                hash(model["Code"] + entity["Code"]): {
                    "Id": entity["Id"],
                    "Name": entity["Name"],
                    "Code": entity["Code"],
                    "IdModel": model["Id"],
                    "NameModel": model["Name"],
                    "CodeModel": model["Code"],
                }
            }
            self.entities.update(dict_entity)
            edge_entity_file = {
                "source": file_RETW,
                "target": hash(model["Code"] + entity["Code"]),
                "creates": True,
            }
            self.edges.append(edge_entity_file)

    def _add_mappings(self, file_RETW: str, mappings: dict):
        for mapping in mappings:
            dict_entity = {
                hash(model["Code"] + entity["Code"]): {
                    "Id": entity["Id"],
                    "Name": entity["Name"],
                    "Code": entity["Code"],
                    "IdModel": model["Id"],
                    "NameModel": model["Name"],
                    "CodeModel": model["Code"],
                }
            }
            dict_entity = {
                hash(model["Code"] + entity["Code"]): {
                    "Id": entity["Id"],
                    "Name": entity["Name"],
                    "Code": entity["Code"],
                    "IdModel": model["Id"],
                    "NameModel": model["Name"],
                    "CodeModel": model["Code"],
                }
            }


def main():
    """Main function to process RETW files and generate mapping order and DAG visualizations.

    Processes a list of RETW files, adds them to a MappingDependencies object,
    and generates the mapping order and DAG visualization for each iteration of adding a file.
    """
    lst_files_RETW = ["output/Usecase_Aangifte_Behandeling.json"]
    graph_RETWs = Graph_RETW_Files()
    graph_RETWs.add_RETW_files(files_RETW=lst_files_RETW)


if __name__ == "__main__":
    main()
