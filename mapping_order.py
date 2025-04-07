from collections import defaultdict
import json

import igraph as ig
import networkx as nx
from pyvis.network import Network

from log_config import logging

logger = logging.getLogger(__name__)

# TODO: Keeping a trail of files added to the dependencies


class MappingDependencies:
    def __init__(self):
        """Initialize MappingDependencies.

        Initializes the nodes, links, and key lists for mappings and entities.
        """
        self.nodes = []
        self.links = []
        self.keys_mapping = [
            "Id",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
        ]
        self.keys_entity = [
            "Id",
            "Name",
            "Code",
            "IdModel",
            "NameModel",
            "CodeModel",
            "IsDocumentModel",
        ]

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

        if "Mappings" in dict_RETW:
            lst_mappings = dict_RETW["Mappings"]
            for mapping in lst_mappings:
                self._add_mapping(dict_mapping=mapping)
        else:
            logger.warning(f"Couldn't find mappings in RETW file '{file_RETW}'")

        return True

    def _add_mapping(self, dict_mapping: dict) -> bool:
        """Create nodes and edges based on mapping

        Args:
            dict_mapping (dict): RETW mapping
        """
        # Create a node from the mapping information
        node_mapping = self._create_mapping_node(dict_mapping)

        # Create nodes for target and source entities
        if "EntityTarget" in dict_mapping:
            node_target = self._create_target_node(
                dict_mapping["EntityTarget"], entity_keys=self.keys_entity
            )
        else:
            logger.error(
                f"Could not find target entity for mapping '{dict_mapping['Name']}'"
            )
            return False
        if "SourceComposition" in dict_mapping:
            nodes_source = self._create_source_nodes(
                dict_mapping["SourceComposition"], entity_keys=self.keys_entity
            )
        else:
            return False

        # Create links
        self.links.append(
            {"source": node_mapping["name"], "target": node_target["name"]}
        )
        links_source = [
            {"source": node["name"], "target": node_mapping["name"]}
            for node in nodes_source
        ]
        self.links = self.links + links_source

        # Combine nodes
        lst_tmp_nodes = self.nodes + nodes_source + [node_mapping] + [node_target]
        # Make sure only unique nodes are added (entities can be part of multiple mappings)
        self.nodes = list({v["name"]: v for v in lst_tmp_nodes}.values())
        return True

    def _create_mapping_node(self, mapping: dict) -> dict:
        """Create a node for the mapping

        Args:
            mapping (dict): Mapping data

        Returns:
            dict: Mapping data, excluding source and entity data
        """
        node = {key: mapping[key] for key in self.keys_mapping}
        node["name"] = node["Id"]
        node["role"] = "mapping"
        return node

    def _create_target_node(self, entity_target: dict, entity_keys: list) -> dict:
        """Create a node for the target entity of a mapping.

        Creates a node dictionary for the target entity, including relevant entity data.

        Args:
            entity_target (dict): Data on the target entity.
            entity_keys (list): Entity data to include in the node.

        Returns:
            dict: Node data for the target entity.
        """
        node = {key: entity_target[key] for key in entity_keys if key in entity_target}
        node["name"] = node["Id"]
        node["role"] = "entity"
        return node

    def _create_source_nodes(self, entity_sources: list, entity_keys: list) -> list:
        """Add nodes to the list for entities that are input for a mapping

        Args:
            entity_sources (list): Dictionaries for the source entities
            entity_keys (list): Properties of an entity that should be added as node attributes

        Returns:
            list: Nodes with data for input entities
        """
        lst_nodes = []
        for source in entity_sources:
            source_entity = source["Entity"]
            node = {
                key: source_entity[key] for key in entity_keys if key in source_entity
            }
            node["name"] = node["Id"]
            node["role"] = "entity"
            lst_nodes.append(node)
        return lst_nodes

    def get_mapping_order(self) -> list:
        """Returns mappings and order of running (could be parallel,
        in which case other subsorting should be implemented if needed)

        Returns:
            list: List of mappings with order
        """
        lst_mappings = []
        dag = self.get_dag()
        for node in dag.vs:
            if node["role"] == "mapping":
                dict_mapping = {key: node[key] for key in self.keys_mapping}
                dict_mapping["RunOrder"] = node["run_level"]
                lst_mappings.append(dict_mapping)
        # Sort the list of mappings by run order and the id
        sorting = sorted([(i["RunOrder"], i["Id"], i) for i in lst_mappings])
        lst_mappings = [i[2] for i in sorting]
        return lst_mappings

    def get_dag(self) -> ig.Graph:
        """Turns mappings into a Directed Graph and add derived data

        Returns:
            ig.Graph: Directed graph of the mappings and entities involved
        """
        dag = ig.Graph.DictList(edges=self.links, vertices=self.nodes, directed=True)
        if not dag.is_dag():
            logger.error(
                "Graph is cyclic, ETL mappings should always be acyclic! https://en.wikipedia.org/wiki/Directed_acyclic_graph"
            )
        dag = self._dag_node_position(dag=dag)
        dag = self._dag_mapping_run_level(dag=dag)
        dag = self._dag_node_hierarchy_level(dag=dag)
        dag = self._set_dag_visual_attributes(dag=dag)
        return dag

    def _dag_node_position(self, dag: ig.Graph) -> ig.Graph:
        """Determine and set the position of each node in the DAG.

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
        for qty_in, qty_out, role in zip(
            dag.vs["qty_in"], dag.vs["qty_out"], dag.vs["role"]
        ):
            if qty_in == 0 and qty_out > 0:
                position = "start"
            elif qty_in > 0 and qty_out > 0:
                position = "intermediate"
            elif qty_in > 0 and qty_out == 0:
                position = "end"
            else:
                position = "undetermined"
            lst_entity_position.append(position)
        dag.vs["position"] = lst_entity_position
        return dag

    def _dag_mapping_run_level(self, dag: ig.Graph) -> ig.Graph:
        """Erich the DAG with the sequence the mappings should run in

        Args:
            dag (ig.Graph): DAG that describes entities and mappings

        Returns:
            ig.Graph: DAG where the vertices are enriched with the attribute 'run_level',
            entity vertices get the value -1
        """
        lst_mapping_order = []
        for i in range(dag.vcount()):
            lst_vertices = dag.subcomponent(dag.vs[i], mode="in")
            predecessors = [dag.vs[vtx] for vtx in lst_vertices]
            predecessors_mapping = [
                vtx for vtx in predecessors if vtx["role"] == "mapping"
            ]
            lst_mapping_order.append(len(predecessors_mapping) - 1)
        # Assign valid run order to mappings only
        lst_run_level = []
        lst_run_level.extend(
            run_level if role == "mapping" else -1
            for run_level, role in zip(lst_mapping_order, dag.vs["role"])
        )
        dag.vs["run_level"] = lst_run_level
        dag = self._mapping_stages(dag=dag)
        return dag

    def _mapping_stages(self, dag: ig.Graph) -> ig.Graph:
        """Determine mapping stages for each level

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
            mappings = nodes_mapping.select(run_level_eq=run_level)
            mapping_sources = [
                {"mapping": mapping["Id"], "sources": dag.predecessors(mapping)}
                for mapping in mappings
            ]
            # Create graph of mapping conflicts (mappings that draw on the same sources)
            lst_vertices = [{"name": mapping["mapping"]} for mapping in mapping_sources]
            lst_edges = []
            for a in mapping_sources:
                for b in mapping_sources:
                    if a["mapping"] < b["mapping"]:
                        qty_common = len(set(a["sources"]) & set(b["sources"]))
                        if qty_common > 0:
                            lst_edges.append({"source": a["mapping"], "target": b["mapping"]})
            graph_conflicts = ig.Graph.DictList(vertices=lst_vertices, edges=lst_edges, directed=False)
            # Determine unique sorting for conflicts
            order = graph_conflicts.vertex_coloring_greedy(method='colored_neighbors')
            dict_level_runs |= dict(zip(graph_conflicts.vs["name"], order))

        # TODO: add result back to DAG
        return dag

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

    def _set_dag_visual_attributes(self, dag: ig.Graph) -> ig.Graph:
        """Sets visual attributes for nodes in the dag

        Args:
            dag (ig.Graph): _description_

        Returns:
            ig.Graph: _description_
        """
        dag = self._set_nodes_label(dag=dag)
        dag = self._set_nodes_color(dag=dag)
        dag = self._set_nodes_shape(dag=dag)
        return dag

    def _set_nodes_label(self, dag: ig.Graph) -> ig.Graph:
        """Set the label for each node in the DAG.

        Assigns labels to nodes based on their run order and name.
        Mappings have their run order prepended to the label.

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with node labels set.
        """
        for i, order in enumerate(dag.vs["run_level"]):
            if order >= 0:
                dag.vs[i]["label"] = str(order) + "\n" + dag.vs[i]["Name"]
            else:
                dag.vs[i]["label"] = dag.vs[i]["Name"]
        return dag

    def _set_nodes_shape(self, dag: ig.Graph) -> ig.Graph:
        """Set the shape of each node in the DAG based on its role.

        Assigns shapes to nodes for visual differentiation based on whether they are mappings or entities.

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with node shapes set.
        """
        node_shapes = {
            "entity": "circle",
            "mapping": "hexagon",
        }
        dag.vs["shape"] = [node_shapes[type_key] for type_key in dag.vs["role"]]
        return dag

    def _set_nodes_color(self, dag: ig.Graph) -> ig.Graph:
        """Set the color of each node in the DAG based on its role and position.

        Assigns colors to nodes for visual differentiation based on whether they are mappings or entities,
        and their position in the DAG (start, intermediate, end).

        Args:
            dag (ig.Graph): The DAG to process.

        Returns:
            ig.Graph: The DAG with node colors set.
        """
        node_colors = {
            "start": "gold",
            "intermediate": "yellowgreen",
            "end": "lawngreen",
            "mapping": "slateblue",
            "undetermined": "red",
        }
        for i in range(dag.vcount()):
            if dag.vs[i]["role"] == "mapping":
                dag.vs[i]["color"] = node_colors[dag.vs[i]["role"]]
            else:
                dag.vs[i]["color"] = node_colors[dag.vs[i]["position"]]
        return dag

    def plot_dag(self, dag: ig.Graph, file_png_out: str) -> None:
        """Creates an image of the DAG

        Args:
            dag (ig.Graph): DAG of mappings and entities
            file_png_out (str): file name to write the image to
        """
        layout = dag.layout_sugiyama()
        visual_style = {"bbox": (1920, 1080), "margin": 100}
        ig.plot(dag, target=file_png_out, layout=layout, directed=True, **visual_style)

    def _igraph_to_networkx(self, dag: ig.Graph) -> nx.DiGraph:
        """Converts an igraph into a networkx graph

        Args:
            dag (ig.Graph): igraph graph

        Returns:
            nx.DiGraph: networkx graph
        """
        dag_nx = nx.DiGraph()
        # Convert nodes
        lst_nodes_igraph = dag.get_vertex_dataframe().to_dict("records")
        lst_nodes = []
        lst_nodes.extend((node["name"], node) for node in lst_nodes_igraph)
        dag_nx.add_nodes_from(lst_nodes)

        # Convert edges
        lst_edges_igraph = dag.get_edge_dataframe().to_dict("records")
        lst_edges = []
        lst_edges.extend((edge["source"], edge["target"]) for edge in lst_edges_igraph)
        dag_nx.add_edges_from(lst_edges)
        return dag_nx

    def get_dag_networkx(self) -> nx.DiGraph:
        dag = self.get_dag()
        dag = self._set_pyvis_attributes(dag=dag)
        return self._igraph_to_networkx(dag=dag)

    def _set_pyvis_attributes(self, dag: ig.Graph) -> ig.Graph:
        # Set visual node properties
        for node in dag.vs:
            node["shape"] = "database" if node["role"] == "entity" else "hexagon"
            node["shadow"] = True
            node["label"] = str(node["run_level"]) if node["run_level"] >= 0 else ""
            self._set_pyvis_node_tooltip(node)
        # Set edge attributes
        # FIXME: does nothing at the moment, lost in igraph to networkx conversion
        for edge in dag.es:
            edge["color"] = "darkslategrey"
            edge["shadow"] = True
        return dag

    def _set_pyvis_node_tooltip(self, node: ig.Vertex):
        """Set the tooltip for a node in the pyvis visualization.

        Sets the 'title' attribute of the node, which is used as a tooltip in pyvis,
        containing detailed information about the node.

        Args:
            node (ig.Vertex): The node to set the tooltip for.
        """
        node["title"] = f"""Type: {node["role"]}\n
                    Id: {node["name"]}
                    Name: {node["Name"]}
                    Code: {node["Code"]}
                """
        if node["role"] == "mapping":
            node["title"] = (
                node["title"]
                + f"""
                    Run order: {str(node["run_level"])}
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
                Name Model: {node["NameModel"]}
                Code Model: {node["CodeModel"]}
                Is Target: {node["IsDocumentModel"]}
                """
            )

    def plot_dag_networkx(self, dag: nx.DiGraph, file_html_out: str) -> None:
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
    dep_parser = MappingDependencies()

    for i, file_RETW in enumerate(lst_files_RETW):
        # Add file to parser
        if dep_parser.add_RETW_file(file_RETW=file_RETW):
            logger.info(f"Added RETW file '{file_RETW}'")
            # Write mapping
            lst_mapping_order = dep_parser.get_mapping_order()
            with open(
                f"output/mapping_order_{str(i)}.jsonl", "w", encoding="utf-8"
            ) as file:
                for mapping in lst_mapping_order:
                    json.dump(mapping, file)
                    file.write("\n")

            # Write HTML overview
            dag = dep_parser.get_dag_networkx()
            dep_parser.plot_dag_networkx(
                dag, file_html_out=f"output/dag_structure_{str(i)}.html"
            )
        else:
            logger.error(f"Failed to add RETW file '{file_RETW}'")
            return


if __name__ == "__main__":
    main()
