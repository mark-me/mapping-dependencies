from enum import Enum, auto

import igraph as ig
import networkx as nx

from log_config import logging

logger = logging.getLogger(__name__)


class EdgeType(Enum):
    """Enumerates the types of edges in the graph.

    Provides distinct identifiers for each type of edge in the graph, representing relationships between files, mappings, and entities.
    """

    FILE_ENTITY = auto()
    FILE_MAPPING = auto()
    ENTITY_SOURCE = auto()
    ENTITY_TARGET = auto()


class VertexType(Enum):
    """Enumerates the types of vertices in the graph.

    Provides distinct identifiers for each type of node in the graph, including entities, mappings, and files.
    """

    ENTITY = auto()
    MAPPING = auto()
    FILE = auto()
    ERROR = auto()


class GraphRETWBase:
    def __init__(self):
        self.igraph_type_shape = {
            VertexType.ENTITY.name: "square",
            VertexType.FILE.name: "triangle",
            VertexType.MAPPING.name: "circle",
            VertexType.ERROR.name: "triangle-down",
        }
        self.pyvis_type_shape = {
            VertexType.ENTITY.name: "database",
            VertexType.FILE.name: "square",
            VertexType.MAPPING.name: "hexagon",
            VertexType.ERROR.name: "star",
        }
        self.node_type_color = {
            VertexType.ENTITY.name: "gold",
            VertexType.FILE.name: "silver",
            VertexType.MAPPING.name: "slateblue",
            VertexType.ERROR.name: "red",
        }
        self.node_position_color = {}

    def igraph_to_networkx(self, graph: ig.Graph) -> nx.DiGraph:
        """Converts an igraph into a networkx graph

        Args:
            dag (ig.Graph): igraph graph

        Returns:
            nx.DiGraph: networkx graph
        """
        dag_nx = nx.DiGraph()
        # Convert nodes
        lst_nodes_igraph = graph.get_vertex_dataframe().to_dict("records")
        lst_nodes = []
        lst_nodes.extend((node["name"], node) for node in lst_nodes_igraph)
        dag_nx.add_nodes_from(lst_nodes)

        # Convert edges
        lst_edges_igraph = graph.get_edge_dataframe().to_dict("records")
        lst_edges = []
        lst_edges.extend((edge["source"], edge["target"]) for edge in lst_edges_igraph)
        dag_nx.add_edges_from(lst_edges)
        return dag_nx
