from enum import Enum, auto

import igraph as ig
import networkx as nx
from pyvis.network import Network

from log_config import logging

logger = logging.getLogger(__name__)


class VertexType(Enum):
    """Enumerates the types of vertices in the graph.

    Provides distinct identifiers for each type of node in the graph, including entities, mappings, and files.
    """

    ENTITY = auto()
    MAPPING = auto()
    FILE_RETW = auto()
    ATTRIBUTE = auto()
    ERROR = auto()


class EdgeType(Enum):
    """Enumerates the types of edges in the graph.

    Provides distinct identifiers for each type of edge in the graph, representing relationships between files, mappings, and entities.
    """

    FILE_ENTITY = auto()
    FILE_MAPPING = auto()
    ENTITY_SOURCE = auto()
    ENTITY_TARGET = auto()
    ENTITY_ATTRIBUTE = auto()
    ATTRIBUTE_SOURCE = auto()
    ATTRIBUTE_TARGET = auto()

class GraphRETWBase:
    def __init__(self):
        self.igraph_type_shape = {
            VertexType.ENTITY.name: "square",
            VertexType.ATTRIBUTE.name: "star",
            VertexType.FILE_RETW.name: "triangle",
            VertexType.MAPPING.name: "circle",
            VertexType.ERROR.name: "triangle-down",
        }
        self.pyvis_type_shape = {
            VertexType.ENTITY.name: "database",
            VertexType.ATTRIBUTE.name: "diamond",
            VertexType.FILE_RETW.name: "square",
            VertexType.MAPPING.name: "hexagon",
            VertexType.ERROR.name: "star",
        }
        self.node_type_color = {
            VertexType.ENTITY.name: "gold",
            VertexType.ATTRIBUTE.name: "slategray",
            VertexType.FILE_RETW.name: "silver",
            VertexType.MAPPING.name: "slateblue",
            VertexType.ERROR.name: "red",
        }


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

    def plot_graph_html(self, graph: ig.Graph, file_html: str) -> None:
        """Create a html file with a graphical representation of a networkx graph

        Args:
            dag (nx.DiGraph): Networkx DAG
            file_html_out (str): file path that the result should be written to
        """
        net = Network("900px", "1917px", directed=True, layout=True)
        graph = self.igraph_to_networkx(graph=graph)
        net.from_nx(graph)
        net.options.layout.hierarchical.sortMethod = "directed"
        net.options.physics.solver = "hierarchicalRepulsion"
        net.options.edges.smooth = False
        net.options.interaction.navigationButtons = True
        net.toggle_physics(True)
        for edge in net.edges:
            edge["shadow"] = True
        net.show(file_html, notebook=False)