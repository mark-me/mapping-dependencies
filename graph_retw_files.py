import json
from pathlib import Path

import igraph as ig

from graph_base import EdgeType, GraphRETWBase, VertexType
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

    def add_RETW_files(self, files_RETW: list) -> bool:
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
                    "type": VertexType.FILE_RETW.name,
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

    def _set_attributes_pyvis(self, graph: ig.Graph) -> ig.Graph:
        """Set attributes for pyvis visualization.

        Sets the shape, shadow, color, and tooltip for each node in the graph
        based on their type and other properties. Also sets the shadow for edges.

        Args:
            graph (ig.Graph): The igraph graph to set attributes for.

        Returns:
            ig.Graph: The graph with attributes set for pyvis visualization.
        """
        for node in graph.vs:
            node["shape"] = self.pyvis_type_shape[node["type"]]
            node["shadow"] = True
            node["color"] = self.node_type_color[node["type"]]
            self._set_node_tooltip_pyvis(node)
        # Set edge attributes
        # FIXME: does nothing at the moment, lost in igraph to networkx conversion
        for edge in graph.es:
            edge["shadow"] = True
        return graph

    def _set_node_tooltip_pyvis(self, node: ig.Vertex) -> None:
        """Set the tooltip for a node in the pyvis visualization.

        Sets the 'title' attribute of the node, which is used as a tooltip in pyvis,
        containing detailed information about the node.

        Args:
            node (ig.Vertex): The node to set the tooltip for.
        """
        if node["type"] == VertexType.FILE_RETW.name:
            node["title"] = f"""FileRETW: {node["FileRETW"]}
                    Order: {node["Order"]}
                    Created: {node["TimeCreated"]}
                    Modified: {node["TimeModified"]}"""
        if node["type"] in [VertexType.MAPPING.name, VertexType.ENTITY.name]:
            node["title"] = f"""Name: {node["Name"]}
                        Code: {node["Code"]}
                        Id: {node["Id"]}
                    """
        if node["type"] == VertexType.MAPPING.name:
            node["title"] = (
                node["title"]
                + f"""
                    CreationDate: {node["CreationDate"]}
                    Creator: {node["Creator"]}
                    ModificationDate: {node["ModificationDate"]}
                    Modifier: {node["Modifier"]}
                """
            )
        elif node["type"] == VertexType.ENTITY.name:
            node["title"] = node["title"] + f"Model: {node['CodeModel']}"

    def plot_graph_total(self, file_html: str) -> None:
        """Plot the total graph and save it to an HTML file.

        Builds the total graph, sets pyvis attributes, and visualizes it in an HTML file.

        Args:
            file_html (str): The path to the HTML file where the plot will be saved.

        Returns:
            None
        """
        graph = self._build_graph_total()
        graph = self._set_attributes_pyvis(graph=graph)
        self.plot_graph_html(graph=graph, file_html=file_html)


    def plot_graph_retw_file(self, file_retw: str, file_html: str) -> None:
        """Plot the graph for a specific RETW file.

        Builds the total graph, selects the subgraph related to a specific RETW file,
        sets pyvis attributes, and visualizes it in an HTML file.

        Args:
            file_retw (str): Path to the RETW file.
            file_html (str): Path to the output HTML file.

        Returns:
            None
        """
        graph = self._build_graph_total()
        vx_file = graph.vs.select(FileRETW_eq=file_retw)
        vx_file_graph = graph.subcomponent(vx_file[0], mode="out")
        vx_delete = [i for i in graph.vs.indices if i not in vx_file_graph]
        graph.delete_vertices(vx_delete)
        # Visualization
        graph = self._set_attributes_pyvis(graph=graph)
        self.plot_graph_html(graph=graph, file_html=file_html)

    def plot_file_dependencies(self, file_html: str) -> None:
        graph = self._build_graph_total()
        vx_files = graph.vs.select(type_eq=VertexType.FILE_RETW.name)

        lst_vertices = [{"name": mapping["mapping"]} for mapping in vx_files]
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

    def plot_entity_journey(
        self, code_model: str, code_entity: str, file_html: str
    ) -> None:
        """Plot the journey of an entity through the graph.

        Builds the total graph, selects a specific entity based on its code and model,
        extracts the subgraph representing the entity's journey (incoming and outgoing connections),
        sets pyvis attributes, converts to NetworkX, and visualizes it in an HTML file.

        Args:
            code_model (str): The code of the model containing the entity.
            code_entity (str): The code of the entity.
            file_html (str, optional): The path to the HTML file where the plot will be saved. Defaults to None.

        Returns:
            None
        """
        graph = self._build_graph_total()
        # Extract graph for relevant entity
        vx_model = graph.vs.select(CodeModel_eq=code_model)
        vx_entity = vx_model.select(Code_eq=code_entity)
        vx_entity_graph = graph.subcomponent(
            vx_entity[0], mode="in"
        ) + graph.subcomponent(vx_entity[0], mode="out")
        vx_delete = [i for i in graph.vs.indices if i not in vx_entity_graph]
        graph.delete_vertices(vx_delete)
        # Visualization
        graph = self._set_attributes_pyvis(graph=graph)
        # Recolor requested entity
        vx_model = graph.vs.select(CodeModel_eq=code_model)
        vx_entity = vx_model.select(Code_eq=code_entity)
        graph.vs[vx_entity.indices[0]]["color"] = "lightseagreen"
        self.plot_graph_html(graph=graph, file_html=file_html)


def main():
    """Main function to process RETW files and generate mapping order and DAG visualizations.

    Processes a list of RETW files, adds them to a MappingDependencies object,
    and generates the mapping order and DAG visualization for each iteration of adding a file.
    """
    lst_files_RETW = [
        "output/Usecase_Aangifte_Behandeling(1).json",
        "output/Usecase_Test_BOK.json",
    ]
    graph = GraphRETWFiles()
    graph.add_RETW_files(files_RETW=lst_files_RETW)
    graph.plot_graph_total(file_html="output/graph_files_total.html")
    graph.plot_entity_journey(
        code_model="Da_Central_CL",
        code_entity="DmsProcedure",
        file_html="output/entity_journey.html",
    )
    #graph.plot_file_dependencies(file_html="output/file_dependencies.html")


if __name__ == "__main__":
    main()
