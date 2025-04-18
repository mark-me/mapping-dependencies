import igraph as ig

from log_config import logging
from dag_etl import EtlDag, VertexType, NoFlowError

logger = logging.getLogger(__name__)


class ETLFailureSimulator(EtlDag):
    def __init__(self):
        """Initialize the MappingSimulator.

        Initializes the DAG, list of failed nodes, and list of affected nodes.
        """
        super().__init__()
        self.dag = ig.Graph()
        self.nodes_failed = []
        self.nodes_affected = []

    def _derive_affected(self) -> ig.Graph:
        """Update the DAG to reflect the impact of failed nodes.

        Identifies and marks nodes affected by the failures, updating their visual attributes (color, shape) in the DAG.

        Returns:
            ig.Graph: The updated DAG.
        """
        nodes_affected = []
        for node_failed in self.nodes_failed:
            nodes_affected = nodes_affected + self.dag.subcomponent(
                node_failed, mode="out"
            )
        self.nodes_affected = list(set(nodes_affected))
        # Set visual attributes accordingly
        self._set_attributes_pyvis(dag=self.dag)
        for id_node in self.nodes_affected:
            node = self.dag.vs[id_node]
            if id_node in self.nodes_failed:
                node["color"] = "red"
                node["shape"] = "star"
            else:
                node["color"] = "tomato"

    def set_entities_failed(self, node_ids: list) -> None:
        """Sets the status of an entity (or mapping) to failed, and derives the consequences in the ETL DAG.

        Args:
            id (str): The 'o' identifier of an object

        Returns:
            nx.DiGraph: A networkx graph with the failure and it's consequences.
        """
        try:
            self.dag = self._build_dag_mappings()
        except NoFlowError:
            logger.error("There are no mappings, so there is no ETL flow to plot!")
            return
        for node_id in node_ids:
            self.nodes_failed.append(self.dag.vs.find(Id=node_id).index)
        self._derive_affected()

    def _get_affected_nodes(self, filter_type: str) -> dict:
        """Get the nodes in the DAG, categorized by failures and affected.

        Args:
            filter_role (str): Indicates whether mapping(s) or entity(s) should be returned

        Returns:
            dict: nodes affected by the failure, categorized by failures and affected.
        """
        dict_results = {}
        lst_failed = []
        lst_affected = []
        for id_node in self.nodes_affected:
            node = self.dag.vs[id_node]
            if node["type"] == filter_type:
                dict_mapping = {key: node[key] for key in node.attribute_names()}
                if id_node in self.nodes_failed:
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
            "Mappings": self._get_affected_nodes(filter_type=VertexType.MAPPING.name),
            "Entities": self._get_affected_nodes(filter_type=VertexType.ENTITY.name),
        }
        return dict_fallout

    def plot_dag_fallout(self, file_html: str) -> None:
        self._set_attributes_pyvis(dag=self.dag)
        self._derive_affected()
        self.plot_graph_html(graph=self.dag, file_html=file_html)
