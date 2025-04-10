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

    def _build_dag_mappings(self) -> ig.Graph:
        vertices = list(self.mappings.values()) + list(self.entities.values())
        edge_types = [EdgeType.ENTITY_SOURCE, EdgeType.ENTITY_TARGET]
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
                position = ObjectPosition.START
            elif qty_in > 0 and qty_out > 0:
                position = ObjectPosition.INTERMEDIATE
            elif qty_in > 0 and qty_out == 0:
                position = ObjectPosition.END
            else:
                position = ObjectPosition.UNDETERMINED
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
                dag.vs[vtx]["role"] == "mapping"
                for vtx in dag.subcomponent(dag.vs[i], mode="in")
            )
            - 1
            for i in range(dag.vcount())
        ]
        # Assign valid run order to mappings only
        lst_run_level = []
        lst_run_level.extend(
            run_level if role == "mapping" else -1
            for run_level, role in zip(lst_mapping_order, dag.vs["role"])
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
        nodes_mapping = dag.vs.select(role_eq="mapping")

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
                [vtx for vtx in lst_vertices if dag.vs[vtx]["role"] == "mapping"]
            )
            if dag.vs[i]["role"] == "entity" and level == 1:
                level = 2
            elif dag.vs[i]["role"] == "mapping" and level > 1:
                level += 1
            elif dag.vs[i]["role"] == "entity" and level > 1:
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
            if dag.vs[vtx]["position"] == "end"
        )
        for i in range(dag.vcount()):
            if dag.vs[i]["position"] == "end":
                dag.vs[i]["level"] = level_max
        return dag

    def plot_dag_html(self, dag: nx.DiGraph, file_html_out: str) -> None:
        """Create a html file with a graphical representation of a networkx graph

        Args:
            dag (nx.DiGraph): Networkx DAG
            file_html_out (str): file path that the result should be written to
        """
        net = Network("900px", "1917px", directed=True, layout=True)
        net.from_nx(dag)
        net.options.layout.hierarchical.sortMethod = "directed"
        net.options.physics.solver = "hierarchicalRepulsion"
        net.options.edges.smooth = False
        net.options.interaction.navigationButtons = True
        net.toggle_physics(True)
        for edge in net.edges:
            edge["shadow"] = True
        net.show(file_html_out, notebook=False)


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


if __name__ == "__main__":
    main()
