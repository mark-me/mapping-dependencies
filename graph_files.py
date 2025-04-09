import json
from pathlib import Path

import igraph as ig

from graphs_base import EdgeType, GraphRETWBase, VertexType
from log_config import logging

logger = logging.getLogger(__name__)


class GraphRETWFiles(GraphRETWBase):
    """Represents a graph of RETW files, mappings, and entities.

    This class extends GraphRETWBase and provides functionalities to build and visualize a graph
    representing relationships between RETW files, mappings, and entities.
    """
    def __init__(self):
        """Initializes a new instance of the GraphRETWFiles class.

        Initializes dictionaries to store files, entities, and mappings, a list for edges, and an igraph graph object.
        """
        super().__init__()
        self.files_RETW = {}
        self.entities = {}
        self.mappings = {}
        self.edges = []
        self.graph = ig.Graph()

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
        files_RETW = list(set(files_RETW))

        # Process files
        for file_RETW in files_RETW:
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
        order_added = len(self.files_RETW)
        id_file = hash(file_RETW)
        self.files_RETW.update(
            {
                id_file: {
                    "name": id_file,
                    "type": VertexType.FILE.name,
                    "Order": order_added,
                    "FileRETW": file_RETW,
                    "TimeCreated": Path(file_RETW).stat().st_ctime,
                    "TimeModified": Path(file_RETW).stat().st_mtime,
                }
            }
        )
        self._add_model_entities(id_file=id_file, dict_RETW=dict_RETW)
        self._add_mappings(id_file=id_file, mappings=dict_RETW["Mappings"])
        return True

    def _add_model_entities(self, id_file: int, dict_RETW: list) -> None:
        """Add model entities to the graph.

        Extracts entities from the document model in the RETW dictionary and adds them as nodes to the graph.
        Also adds edges between the file and its entities.

        Args:
            file_RETW (str): Path to the RETW file.
            dict_RETW (list): Dictionary containing RETW data.

        Returns:
            None
        """
        # Determine document model
        model = [
            model for model in dict_RETW["Models"] if model["IsDocumentModel"] is True
        ][0]
        if "Entities" not in model:
            logger.warning(f"No entities for a document model in '{id_file}'")
            return

        for entity in model["Entities"]:
            id_entity = hash(model["Code"] + entity["Code"])
            dict_entity = {
                id_entity: {
                    "name": id_entity,
                    "type": VertexType.ENTITY.name,
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
                "source": id_file,
                "target": id_entity,
                "type": EdgeType.FILE_ENTITY.name,
                "CreationDate": entity["CreationDate"],
                "Creator": entity["Creator"],
                "ModificationDate": entity["ModificationDate"],
                "Modifier": entity["Modifier"],
            }
            self.edges.append(edge_entity_file)

    def _add_mappings(self, id_file: int, mappings: dict) -> None:
        """Add mappings to the graph.

        Processes each mapping extracted from the RETW dictionary, adds them as nodes to the graph,
        and establishes edges between the file and its mappings, as well as between mappings and their
        source and target entities.

        Args:
            file_RETW (str): Path to the RETW file.
            mappings (dict): Dictionary containing mapping data.

        Returns:
            None
        """
        for mapping_RETW in mappings:
            id_mapping = hash(str(id_file) + mapping_RETW["Id"])
            mapping = {
                id_mapping: {
                    "name": id_mapping,
                    "type": VertexType.MAPPING.name,
                    "Id": mapping_RETW["Id"],
                    "Name": mapping_RETW["Name"],
                    "Code": mapping_RETW["Code"],
                    "CreationDate": mapping_RETW["CreationDate"],
                    "Creator": mapping_RETW["Creator"],
                    "ModificationDate": mapping_RETW["ModificationDate"],
                    "Modifier": mapping_RETW["Modifier"],
                }
            }
            self.mappings.update(mapping)
            edge_mapping_file = {
                "source": id_file,
                "target": id_mapping,
                "type": EdgeType.FILE_MAPPING.name,
                "CreationDate": mapping_RETW["CreationDate"],
                "Creator": mapping_RETW["Creator"],
                "ModificationDate": mapping_RETW["ModificationDate"],
                "Modifier": mapping_RETW["Modifier"],
            }
            self.edges.append(edge_mapping_file)
            self._add_mapping_sources(id_mapping=id_mapping, mapping=mapping_RETW)
            self._add_mapping_target(id_mapping=id_mapping, mapping=mapping_RETW)

    def _add_mapping_sources(self, id_mapping: int, mapping: dict) -> None:
        """Add mapping source entities to the graph.

        Iterates through the source composition of a mapping, extracts source entities,
        and adds them as nodes to the graph. Also adds edges between the mapping and its source entities.

        Args:
            id_mapping (int): Unique identifier of the mapping.
            mapping (dict): Dictionary containing mapping data.

        Returns:
            None
        """
        for source in mapping["SourceComposition"]:
            source_entity = source["Entity"]
            id_entity = hash(source_entity["CodeModel"] + source_entity["Code"])
            entity = {
                id_entity: {
                    "name": id_entity,
                    "type": VertexType.ENTITY.name,
                    "Id": source_entity["Id"],
                    "Name": source_entity["Name"],
                    "Code": source_entity["Code"],
                    "IdModel": source_entity["Id"],
                    "CodeModel": source_entity["CodeModel"],
                }
            }
            self.entities.update(entity)
            edge_entity_mapping = {
                "source": id_entity,
                "target": id_mapping,
                "type": EdgeType.ENTITY_SOURCE.name,
            }
            self.edges.append(edge_entity_mapping)

    def _add_mapping_target(self, id_mapping: int, mapping: dict) -> None:
        """Add mapping target entity to the graph.

        Extracts the target entity of a mapping, adds it as a node to the graph,
        and creates an edge between the mapping and its target entity.

        Args:
            id_mapping (int): Unique identifier of the mapping.
            mapping (dict): Dictionary containing mapping data.

        Returns:
            None
        """
        target_entity = mapping["EntityTarget"]
        id_entity = hash(target_entity["CodeModel"] + target_entity["Code"])
        entity = {
            id_entity: {
                "name": id_entity,
                "type": VertexType.ENTITY.name,
                "Id": target_entity["Id"],
                "Name": target_entity["Name"],
                "Code": target_entity["Code"],
                "IdModel": target_entity["Id"],
                "CodeModel": target_entity["CodeModel"],
            }
        }
        self.entities.update(entity)
        edge_entity_mapping = {
            "source": id_mapping,
            "target": id_entity,
            "type": EdgeType.ENTITY_TARGET.name,
        }
        self.edges.append(edge_entity_mapping)

    def _build_graph_total(self) -> ig.Graph:
        """Build the total graph from mappings, entities, and files.

        Constructs an igraph graph using the collected mappings, entities, and files as vertices,
        and the established edges between them.

        Returns:
            ig.Graph: The constructed graph.
        """
        vertices = (
            list(self.mappings.values())
            + list(self.entities.values())
            + list(self.files_RETW.values())
        )
        edges = list(self.edges)
        graph = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        logger.info("Build graph total")
        return graph

    def plot_graph_total(self, file_png: str=None) -> ig.Graph:
        """Plot the total graph and save it to a PNG file.

        Creates the entire graph, including files, mappings, and entities, with appropriate colors and shapes for each node type.
        The visualization can be saved to a specified PNG file.

        Args:
            file_png (str, optional): The path to the PNG file where the plot will be saved. Defaults to None.

        Returns:
            ig.Graph: The graph that was plotted.
        """
        graph = self._build_graph_total()
        # Colouring
        for i in range(graph.vcount()):
            graph.vs[i]["color"] = self.node_type_color[graph.vs[i]["type"]]
            graph.vs[i]["shape"] = self.igraph_type_shape[graph.vs[i]["type"]]
        logger.info(f"Wrote total graph to '{file_png}'")
        if file_png is not None:
            ig.plot(graph, file_png)
        return graph

    def _build_dag_mappings(self) -> ig.Graph:
        vertices = (
            list(self.mappings.values())
            + list(self.entities.values())
        )
        edge_types = [EdgeType.ENTITY_SOURCE.name, EdgeType.ENTITY_TARGET.name]
        edges = [v for v in self.edges if v["type"] in edge_types]
        dag = ig.Graph.DictList(vertices=vertices, edges=edges, directed=True)
        dag = self._dag_node_position(dag=dag)
        logger.info("Build graph total")
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
        for qty_in, qty_out in zip(
            dag.vs["qty_in"], dag.vs["qty_out"]
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

    def plot_dag_mappings(self, file_png: str=None) -> ig.Graph:
        """Plot the total graph and save it to a PNG file.

        Creates the entire graph, including files, mappings, and entities, with appropriate colors and shapes for each node type.
        The visualization can be saved to a specified PNG file.

        Args:
            file_png (str, optional): The path to the PNG file where the plot will be saved. Defaults to None.

        Returns:
            ig.Graph: The graph that was plotted.
        """
        graph = self._build_dag_mappings()
        # Colouring
        for i in range(graph.vcount()):
            graph.vs[i]["color"] = self.node_type_color[graph.vs[i]["type"]]
            graph.vs[i]["shape"] = self.igraph_type_shape[graph.vs[i]["type"]]
        logger.info(f"Wrote total graph to '{file_png}'")
        if file_png is not None:
            ig.plot(graph, file_png)
        return graph

def main():
    """Main function to process RETW files and generate mapping order and DAG visualizations.

    Processes a list of RETW files, adds them to a MappingDependencies object,
    and generates the mapping order and DAG visualization for each iteration of adding a file.
    """
    lst_files_RETW = ["output/Usecase_Aangifte_Behandeling.json"]
    graph_RETWs = GraphRETWFiles()
    graph_RETWs.add_RETW_files(files_RETW=lst_files_RETW)
    graph = graph_RETWs.plot_graph_total(file_png="output/test_total.png")
    graph = graph_RETWs.plot_dag_mappings(file_png="output/test_mappings.png")

    pass


if __name__ == "__main__":
    main()
