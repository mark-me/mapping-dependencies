from enum import Enum, auto

import igraph as ig
import networkx as nx
from pyvis.network import Network

from graph_files import EdgeType, GraphRETWFiles, VertexType
from log_config import logging

logger = logging.getLogger(__name__)


class ObjectPosition(Enum):
    START = auto()
    INTERMEDIATE = auto()
    END = auto()
    UNDETERMINED = auto()

class DagETL(GraphRETWFiles):
    def __init__(self):
        super().__init__()
        self.node_position_color = {
            ObjectPosition.START.name: "gold",
            ObjectPosition.INTERMEDIATE.name: "yellowgreen",
            ObjectPosition.END.name: "lawngreen",
            ObjectPosition.UNDETERMINED.name: "red",
        }

    def _build_dag_mappings(self) -> ig.Graph:
        vertices = list(self.mappings.values()) + list(self.entities.values())
        edge_types = [EdgeType.ENTITY_SOURCE.name, EdgeType.ENTITY_TARGET.name]
        edges = [v for v in self.edges if v["type"] in edge_types]
        dag = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        dag = self._dag_node_position_category(dag=dag)
        dag = self._calculate_node_levels(dag=dag)
        dag = self._dag_mapping_run_order(dag=dag)
        dag = self._dag_node_hierarchy_level(dag=dag)
        logger.info("Build graph mappings")
        return dag

    def _dag_node_position_category(self, dag: ig.Graph) -> ig.Graph:
        """Determine and set the position category (start, intermediate, end) of each node in the DAG.

        Determines if entities are start, intermediate, or end nodes based on their in-degree and out-degree,
        and adds a 'position' attribute to the DAG vertices.

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with node positions set.
        """
        dag.vs["qty_out"] = dag.degree(dag.vs, mode="out")
        dag.vs["qty_in"] = dag.degree(dag.vs, mode="in")
        lst_entity_position = []
        for qty_in, qty_out in zip(dag.vs["qty_in"], dag.vs["qty_out"]):
            if qty_in == 0 and qty_out > 0:
                position = ObjectPosition.START.name
            elif qty_in > 0 and qty_out > 0:
                position = ObjectPosition.INTERMEDIATE.name
            elif qty_in > 0 and qty_out == 0:
                position = ObjectPosition.END.name
            else:
                position = ObjectPosition.UNDETERMINED.name
            lst_entity_position.append(position)
        dag.vs["position"] = lst_entity_position
        return dag

    def plot_dag_png(self, file_png: str = None) -> ig.Graph:
        """Plot the DAG of all combined mappings and save it to a PNG file.

        Creates the ETL DAG, with mappings and entities for all files, with appropriate colors and shapes for each node type.
        The visualization can be saved to a specified PNG file.

        Args:
            file_png (str, optional): The path to the PNG file where the plot will be saved. Defaults to None.

        Returns:
            ig.Graph: The graph that was plotted.
        """
        graph = self._build_dag_mappings()
        for i in range(graph.vcount()):
            # Coloring
            graph.vs[i]["color"] = self.node_type_color[graph.vs[i]["type"]]
            graph.vs[i]["shape"] = self.igraph_type_shape[graph.vs[i]["type"]]
        logger.info(f"Wrote total graph to '{file_png}'")
        if file_png is not None:
            ig.plot(graph, file_png)
        return graph

    def _dag_mapping_run_order(self, dag: ig.Graph) -> ig.Graph:
        """Erich the DAG with the sequence the mappings should run in

        Args:
            dag (ig.Graph): DAG that describes entities and mappings

        Returns:
            ig.Graph: DAG where the vertices are enriched with the attribute 'run_level',
            entity vertices get the value -1
        """
        # For each node calculate the number of mapping nodes before the current node
        lst_mapping_order = [
            sum(
                dag.vs[vtx]["type"] == VertexType.MAPPING.name
                for vtx in dag.subcomponent(dag.vs[i], mode="in")
            )
            - 1
            for i in range(dag.vcount())
        ]
        # Assign valid run order to mappings only
        lst_run_level = []
        lst_run_level.extend(
            run_level if role == VertexType.MAPPING.name else -1
            for run_level, role in zip(lst_mapping_order, dag.vs["type"])
        )
        dag.vs["run_level"] = lst_run_level
        dag = self._dag_mapping_run_level_stages(dag=dag)
        return dag

    def _dag_mapping_run_level_stages(self, dag: ig.Graph) -> ig.Graph:
        """Determine mapping stages for each run level

        Args:
            dag (ig.Graph): DAG describing the ETL

        Returns:
            ig.Graph: ETL stages for a level added in the mapping vertex attribute 'stage'
        """
        dict_level_runs = {}
        # All mapping nodes
        nodes_mapping = dag.vs.select(type_eq=VertexType.MAPPING.name)

        # Determine run stages of mappings by run level
        run_levels = list({node["run_level"] for node in nodes_mapping})
        for run_level in run_levels:
            # Find run_level mappings and corresponding source entities
            mapping_sources = [
                {"mapping": mapping["Id"], "sources": dag.predecessors(mapping)}
                for mapping in nodes_mapping.select(run_level_eq=run_level)
            ]
            # Create graph of mapping conflicts (mappings that draw on the same sources)
            graph_conflicts = self._dag_run_level_conflicts_graph(mapping_sources)
            # Determine unique sorting for conflicts
            order = graph_conflicts.vertex_coloring_greedy(method="colored_neighbors")
            # Apply them back to the DAG
            dict_level_runs |= dict(zip(graph_conflicts.vs["name"], order))
            for k, v in dict_level_runs.items():
                dag.vs.select(Id_eq=k)["run_level_stage"] = v
        return dag

    def _dag_run_level_conflicts_graph(self, mapping_sources: dict) -> ig.Graph:
        """Generate a graph expressing which mappings share sources

        Args:
            mapping_sources (dict): Mappings with a list of source node ids for each of them

        Returns:
            ig.Graph: Expressing mapping sharing source entities
        """
        lst_vertices = [{"name": mapping["mapping"]} for mapping in mapping_sources]
        lst_edges = []
        for a in mapping_sources:
            for b in mapping_sources:
                if a["mapping"] < b["mapping"]:
                    qty_common = len(set(a["sources"]) & set(b["sources"]))
                    if qty_common > 0:
                        lst_edges.append(
                            {"source": a["mapping"], "target": b["mapping"]}
                        )
        graph_conflicts = ig.Graph.DictList(
            vertices=lst_vertices, edges=lst_edges, directed=False
        )
        return graph_conflicts

    def _dag_node_hierarchy_level(self, dag: ig.Graph) -> ig.Graph:
        """Enrich the DAG with the level in the hierarchy where vertices should be plotted.

        Determines and sets the 'level' attribute for each vertex in the DAG, used for visualization.

        Args:
            dag (ig.Graph): DAG that describes entities and mappings.

        Returns:
            ig.Graph: DAG where the vertices are enriched with the attribute 'level'.
        """
        dag = self._calculate_node_levels(dag)
        dag = self._set_max_end_node_level(dag)
        return dag

    def _calculate_node_levels(self, dag: ig.Graph) -> ig.Graph:
        """Calculate and set the initial level for each node in the DAG.

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with initial node levels set.
        """
        lst_level = []
        for i in range(dag.vcount()):
            lst_vertices = dag.subcomponent(dag.vs[i], mode="in")
            level = len(
                [vtx for vtx in lst_vertices if dag.vs[vtx]["type"] == VertexType.MAPPING.name]
            )
            if dag.vs[i]["type"] == VertexType.ENTITY.name and level == 1:
                level = 2
            elif dag.vs[i]["type"] == VertexType.MAPPING.name and level > 1:
                level += 1
            elif dag.vs[i]["type"] == VertexType.ENTITY.name and level > 1:
                level += 2
            lst_level.append(level)
        dag.vs["level"] = lst_level
        return dag

    def _set_max_end_node_level(self, dag: ig.Graph) -> ig.Graph:
        """Set the level of all end nodes to the maximum level.

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with end node levels adjusted.
        """
        level_max = max(
            dag.vs[vtx]["level"]
            for vtx in range(
                dag.vcount()
            )  # Iterate over all vertices to find the true max level.
            if dag.vs[vtx]["position"] == ObjectPosition.END.name
        )
        for i in range(dag.vcount()):
            if dag.vs[i]["position"] == ObjectPosition.END.name:
                dag.vs[i]["level"] = level_max
        return dag

    def _set_node_attributes_pyvis(self, dag: ig.Graph) -> ig.Graph:
        """Set node and edge attributes for pyvis visualization.

        Sets visual attributes (shape, shadow, tooltip) for nodes and edges in the DAG
        to be used in the pyvis visualization.
        """
        # Set visual node properties
        for node in dag.vs:
            node["shape"] = "database" if node["type"] == VertexType.ENTITY.name else "hexagon"
            node["shadow"] = True
            self._set_node_color_pyvis(node)
            self._set_node_tooltip_pyvis(node)
        # Set edge attributes
        # FIXME: does nothing at the moment, lost in igraph to networkx conversion
        for edge in dag.es:
            edge["color"] = "darkslategrey"
            edge["shadow"] = True
        return dag

    def _set_node_color_pyvis(self, node: ig.Vertex) -> None:
        """Set the color of each node in the DAG based on its role and position.

        Assigns colors to nodes for visual differentiation based on whether they are mappings or entities,
        and their position in the DAG (start, intermediate, end).

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with node colors set.
        """
        if node["type"] == VertexType.MAPPING.name:
            node["color"] = self.node_type_color[node["type"]]
        else:
            node["color"] = self.node_position_color[node["position"]]

    def _set_node_tooltip_pyvis(self, node: ig.Vertex) -> None:
        """Set the tooltip for a node in the pyvis visualization.

        Sets the 'title' attribute of the node, which is used as a tooltip in pyvis,
        containing detailed information about the node.

        Args:
            node (ig.Vertex): The node to set the tooltip for.
        """
        node["title"] = f"""Type: {node["type"]}\n
                    Id: {node["Id"]}
                    Name: {node["Name"]}
                    Code: {node["Code"]}
                """
        if node["type"] == VertexType.MAPPING.name:
            node["title"] = (
                node["title"]
                + f"""
                    Run level: {str(node["run_level"])}
                    Run level stage: {str(node["run_level_stage"])}
                    CreationDate: {node["CreationDate"]}
                    Creator: {node["Creator"]}
                    ModificationDate: {node["ModificationDate"]}
                    Modifier: {node["Modifier"]}
                """
            )
        else:
            node["title"] = (
                node["title"]
                + f"""
                Id Model: {node["IdModel"]}
                Code Model: {node["CodeModel"]}
                """
            )

    def _get_dag_networkx(self) -> nx.DiGraph:
        """Get the DAG as a NetworkX graph.

        Retrieves the DAG, sets node attributes for pyvis visualization,
        and converts it to a NetworkX graph.

        Returns:
            nx.DiGraph: The DAG as a NetworkX graph.
        """
        dag = self._build_dag_mappings()
        dag = self._set_node_attributes_pyvis(dag=dag)
        return self.igraph_to_networkx(graph=dag)

    def plot_dag_html(self, file_html: str) -> None:
        """Create a html file with a graphical representation of a networkx graph

        Args:
            file_html_out (str): file path that the result should be written to
        """
        dag = self._get_dag_networkx()
        net = Network("900px", "1917px", directed=True, layout=True)
        net.from_nx(dag)
        net.options.layout.hierarchical.sortMethod = "directed"
        net.options.physics.solver = "hierarchicalRepulsion"
        net.options.edges.smooth = False
        net.options.interaction.navigationButtons = True
        net.toggle_physics(True)
        for edge in net.edges:
            edge["shadow"] = True
        net.show(file_html, notebook=False)


def main():
    """Main function to process RETW files and generate mapping order and DAG visualizations.

    Processes a list of RETW files, adds them to a MappingDependencies object,
    and generates the mapping order and DAG visualization for each iteration of adding a file.
    """
    lst_files_RETW = ["output/Usecase_Aangifte_Behandeling.json"]
    file_mappings_png = "output/test_mappings.png"
    file_mappings_html = "output/test_mappings.html"
    dag_ETL = DagETL()
    dag_ETL.add_RETW_files(files_RETW=lst_files_RETW)
    dag_ETL.plot_dag_png(file_png=file_mappings_png)
    dag_ETL.plot_dag_html(file_html=file_mappings_html)


if __name__ == "__main__":
    main()
