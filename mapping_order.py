import json

import igraph as ig
import networkx as nx
import pandas as pd
from pyvis.network import Network

from log_config import logging

logger = logging.getLogger(__name__)


class MappingDependencyParser:
    def __init__(self):
        self.nodes = []
        self.links = []

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
            for mapping in lst_mappings:
                self._add_mapping(dict_mapping=mapping)
        else:
            logger.warning(f"Couldn't find mappings in RETW file '{file}'")

        return True

    def get_dag(self) -> ig.Graph:
        """Turns mappings into a Directed Graph

        Returns:
            ig.Graph: Directed graph of the mappings and entities involved
        """
        dag = ig.Graph.DictList(edges=self.links, vertices=self.nodes, directed=True)

        # Determine running order mappings
        # First determine the number predecessors that are mappings
        lst_order = []
        for i in range(dag.vcount()):
            lst_vertices = dag.subcomponent(dag.vs[i], mode="in")
            test = [dag.vs[vtx] for vtx in lst_vertices]
            vtx_mapping = [vtx for vtx in test if vtx["role"] == "mapping"]
            qty_mapping_predecessors = len(vtx_mapping)
            lst_order.append(qty_mapping_predecessors-1)
        # Assign run order to mappings only
        lst_run_order = []
        for run_order, role in zip(lst_order, dag.vs["role"]):
            lst_run_order.append(run_order if role == "mapping" else -1)
        dag.vs["run_order"] = lst_run_order

        # Determine if entities are intermediates
        dag.vs["qty_out"] = dag.degree(dag.vs, mode="out")
        dag.vs["qty_in"] = dag.degree(dag.vs, mode="in")
        lst_entity_role = []
        for qty_in, qty_out, role in zip(dag.vs["qty_in"], dag.vs["qty_out"], dag.vs["role"]):
            is_intermediate = (qty_in > 0 and qty_out > 0 and role != "mapping")
            lst_entity_role.append('entity_intermediate' if is_intermediate else role)
        dag.vs["role"] = lst_entity_role

        return dag

    def plot_dag(self, dag: ig.Graph, file_png_out: str) -> None:
        """Creates an image of the DAG

        Args:
            dag (ig.Graph): DAG of mappings and entities
            file_png_out (str): file name to write the image to
        """
        # Assign label to nodes
        for i, order in enumerate(dag.vs["run_order"]):
            if order >= 0:
                dag.vs[i]["label"] = str(order) + "\n" + dag.vs[i]["Name"]
            else:
                dag.vs[i]["label"] = dag.vs[i]["Name"]

        node_colors = {
            "entity_source": "yellow",
            "entity_intermediate": "teal",
            "mapping": "green",
            "entity_target": "red",
        }
        dag.vs["color"] = [node_colors[type_key] for type_key in dag.vs["role"]]
        node_shapes = {
            "entity_source": "circle",
            "entity_intermediate": "diamond",
            "mapping": "rectangle",
            "entity_target": "circle",
        }
        dag.vs["shape"] = [node_shapes[type_key] for type_key in dag.vs["role"]]
        layout = dag.layout_sugiyama()
        visual_style = {"bbox": (1920,1080), "margin": 100}
        ig.plot(dag, target=file_png_out, layout = layout, directed=True, **visual_style)

    def plot_dag_interactive(self, dag: ig.Graph, file_png_out: str) -> None:
        df = pd.DataFrame(self.links)
        #df.loc[df["ẗype"] == "mappings", "color"] = "green"
        graph = nx.from_pandas_edgelist(df, )
        nt = Network('1080px', '1920px', directed=True)
        nt.from_nx(graph)
        nt.toggle_physics(True)
        nt.show(file_png_out, notebook=False)
        pass

    def _add_mapping(self, dict_mapping: dict) -> bool:
        """Create nodes and edges based on mapping

        Args:
            dict_mapping (dict): RETW mapping
        """
        # Create a node from the mapping information
        node_mapping = self._create_mapping_node(dict_mapping)

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
            node_target = self._create_target_node(
                dict_mapping["EntityTarget"], entity_keys=keys_entity
            )
        else:
            logger.error(
                f"Could not find target entity for mapping '{dict_mapping['Name']}'"
            )
            return False
        if "SourceComposition" in dict_mapping:
            nodes_source = self._create_source_nodes(
                dict_mapping["SourceComposition"], entity_keys=keys_entity
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
        keys_mapping = [
            "Id",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
        ]
        node = {key: mapping[key] for key in keys_mapping}
        node["name"] = node.pop("Id")
        node["role"] = "mapping"
        return node

    def _create_target_node(self, entity_target: dict, entity_keys: list) -> dict:
        """_summary_

        Args:
            dict_entity_target (dict): Data on the target entity
            lst_entity_keys (list): Entity data to include in the node
        """
        node = {key: entity_target[key] for key in entity_keys if key in entity_target}
        node["name"] = node.pop("Id")
        node["role"] = "entity_target"
        return node

    def _create_source_nodes(self, entity_sources: dict, entity_keys: list) -> list:
        """_summary_

        Args:
            dict_entity_target (dict): _description_
            lst_entity_keys (list): _description_
        """
        lst_nodes = []
        for source in entity_sources:
            source_entity = source["Entity"]
            node = {
                key: source_entity[key] for key in entity_keys if key in source_entity
            }
            node["name"] = node.pop("Id")
            node["role"] = "entity_source"
            lst_nodes.append(node)
        return lst_nodes


if __name__ == "__main__":
    lst_files_RETW = ["output/Usecase_Aangifte_Behandeling.json"]
    dep_parser = MappingDependencyParser()

    for file_RETW in lst_files_RETW:
        success = dep_parser.load_RETW_file(file=file_RETW)
        if success:
            graph = dep_parser.get_dag()
            dep_parser.plot_dag(graph, "output/dag.png")
            #dep_parser.plot_dag_interactive(graph, file_png_out="output/output.html")
