import json

import igraph as ig
import networkx as nx

from log_config import logging
from mapping_order import MappingDependencies

logger = logging.getLogger(__name__)

class MappingSimulator(MappingDependencies):
    def __init__(self):
        super().__init__()
        self.dag = ig.Graph()
        self.node_failed = -1
        self.node_affected = []

    def _derive_affected(self) -> ig.Graph:
        """Changes the DAG to describe the failure of an ETL step and it's consquences

        Returns:
            ig.Graph: _description_
        """
        self.node_affected = self.dag.subcomponent(self.node_failed, mode="out")
        # Set visual attributes accordingly
        self._set_pyvis_attributes(dag=self.dag)
        for id_node in self.node_affected:
            if id_node == self.node_failed:
                self.dag.vs[id_node]["color"] = "red"
                self.dag.vs[id_node]["shape"] = "star"
            else:
                self.dag.vs[id_node]["color"] = "darkorange"

    def set_entity_failed(self, id: str) -> nx.DiGraph:
        """Sets the status of an entity (or mapping) to failed, and derives the consequences in the ETL DAG.

        Args:
            id (str): The 'o' identifier of an object

        Returns:
            nx.DiGraph: A networkx graph with the failure and it's consequences.
        """
        self.dag = self.get_dag()
        self.node_failed = self.dag.vs.find(name=id).index
        self._derive_affected()
        network = self._igraph_to_networkx(dag=self.dag)
        return network

    def _get_affected_nodes(self, filter_role: str) -> dict:
        """Get the nodes in the DAG, categorized by failures and affected.

        Args:
            filter_role (str): Indicates whether mapping(s) or entity(s) should be returned

        Returns:
            dict: nodes affected by the failure, categorized by failures and affected.
        """
        dict_results = {}
        lst_failed = []
        lst_affected = []
        for id_node in self.node_affected:
            node = self.dag.vs[id_node]
            if node["role"] == filter_role:
                dict_mapping = {key: node[key] for key in self.keys_mapping}
                if id_node == self.node_failed:
                    lst_failed.append(dict_mapping)
                else:
                    lst_affected.append(dict_mapping)
        dict_results = {
            "Failed": lst_failed,
            "Affected": lst_affected,
        }
        return dict_results

    def get_report_fallout(self) -> dict:
        """Generates a dictionary reporting on the affected ETL components

        Returns:
            dict: Report on mappings and entities that failed or are affected by the failure
        """
        dict_fallout = {
            "Mappings": self._get_affected_nodes(filter_role="mapping"),
            "Entities": self._get_affected_nodes(filter_role="entity"),
        }
        return dict_fallout


def main():
    lst_files_RETW = ["output/Usecase_Aangifte_Behandeling.json"]
    id_entity_failed = "o71"

    mapping_simulator = MappingSimulator()
    # Adding RETW files to generate complete ETL DAG
    for file_RETW in lst_files_RETW:
        if mapping_simulator.add_RETW_file(file_RETW=file_RETW):
            logger.info(f"Added RETW file '{file_RETW}'")
        else:
            logger.error(f"Failed to add RETW file '{file_RETW}'")
            return

    # Set failed node
    dag = mapping_simulator.set_entity_failed(id=id_entity_failed)
    # Create fallout report file
    dict_fallout = mapping_simulator.get_report_fallout()
    with open("output/dag_run_fallout.json", "w", encoding="utf-8") as file:
        json.dump(dict_fallout, file, indent=4)
    # Create fallout visualization
    mapping_simulator.plot_dag_networkx(
        dag, file_html_out="output/dag_run_report.html"
    )


if __name__ == "__main__":
    main()
