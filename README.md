# Mapping dependency parser

This project analyzes dependencies in an ETL (Extract, Transform, Load) process defined by RETW files. It helps determine the optimal execution order of mappings, identifies potential failures, and visualizes the dependencies between entities and files. The core functionality revolves around building a directed acyclic graph (DAG) representing the ETL flow.

It covers the following broadly:

* what the [ordering of mappings](#determining-mapping-order) should be in the ETL flow, and whether the ETL flow has no closed loops (ETL-flows should be [acyclic](https://en.wikipedia.org/wiki/Directed_acyclic_graph)),
* finding references to entities which are not defined in the processed RETW files,
* the consequences of a failure of a step in ETL process and
* the dependencies between RETW files for entities.

## Running examples

The directory ```dependency_checker``` contains a file ```example.py``` that shows how all classes can be used for the purposes stated above.

The example references contains a list to example RETW files, that are placed in the subdirectory ```retw_examples```. The order of the files in the list is irrelevant to the functionality, so if you could add your own files to the list in a random order.

It uses the class ```DagReporting```, that is defined in the file ```dag_reporting.py```, to create visualizations of:

* the total network of files, entities and mappings,
* a given entity's network of connected files, entities and mappings,
* dependencies between files, based on entities they have in common and,
* a visualization of the ETL flow for all RETW files combined.

It also generates files that contain:

* the ordering of the mappings in an ETL flow and
* the entities which are used in mappings, but lack a definition in one of the files.

It uses the class ```EtlFailure```, which is defined in the file ```dag_etl_failure.py```, to create:

* a visualization of the consequences of a ETL-flow object failing and
* a report on the failing ETL-flow objects

## Implementation documentation

### Determining mapping order

The running order of mappings is determined by two components:

* Run level: where in the Directed Acyclic Graph ([DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph)) hierarchy, going from source entities to end entities, is the mapping positioned. The mappings taking in only source entities are set at run level 0, the next run levels are determined by the number of mappings in the hierarchy running before the mapping under consideration.
* Run level stage: If mappings on the same run level share the same entities they should get different concurrency ordering to prevent deadlocking. A [greedy coloring algorithm](https://www.youtube.com/watch?v=vGjsi8NIpSE) is used to determine the run order of mappings within a run level.

```mermaid
graph LR
  idEa[(Entity a)]
  idEb[(Entity b)]
  idEc[(Entity c)]
  idEd[(Entity d)]
  idEe[(Entity e)]
  idEf[(Entity f)]
  idEg[(Entity g)]
  idEh[(Entity h)]

  subgraph RunLevel: 0
    subgraph RunLevelStage: 0
      idMa{{Mapping a}}
    end
    subgraph RunLevelStage: 1
      idMb{{Mapping b}}
      idMc{{Mapping c}}
    end
  end
  subgraph RunLevel: 1
    subgraph RunLevelStage: 0
      idMd{{Mapping d}}
    end
  end

  idEa --> idMa
  idEb --> idMa
  idMa --> idEe
  idEb --> idMb
  idEc --> idMb
  idMb --> idEf
  idEd --> idMc
  idMc --> idEg
  idEf --> idMd
  idEg --> idMd
  idMd --> idEh
```

### Building the ETL DAG

The mapping dependency parser uses [graphs](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)), more specifically as [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph), which is a network representation of the files, entities (i.e. tables) and mappings. This section explains how the DAG is created.

For each RETW file, the mappings are extracted and the mappings, source- and target entities are turned into nodes (sometimes called vertices). Then there are links created (sometimes called edges) between the source entities and the mappings and the mappings and target entity. If all mappings are parsed into their nodes and edges they can be combined to form a network. This network representation allows the calculations to be performed for the objectives stated in the introduction.

```mermaid
erDiagram
ENTITY ||--|{ MAPPING: "Filled by: ENTITY_TARGET"
MAPPING ||--|{ ENTITY: "Feeds from: ENTITY_SOURCE"
FILE_RETW ||--o{ MAPPING: "Created: FILE_MAPPING"
FILE_RETW ||--o{ ENTITY: "Created: FILE_ENTITY"
```

In a Power Designer document (and the corresponding RETW file), all objects are identified by their 'Id' attribute which for example looks like 'o123'. This Id is internal to a document, but is not suitable for identification when we combine the RETW results of multiple Power Designer documents. For this purpose new identifiers must be created so we have no conflicting identifiers across Power Designer documents, but also maintain integrity where the target entity of one document, might serve as a source entity for a mapping in another Power Designer document. How do is this achieved?

* We assume mappings are unique across Power Designer documents. To build a mapping identifier a hash is applied to the combination of the RETW filename and the mapping object code.
* To maintain consistency identification of entities across Power Designer documents a hash is applied to the combination of the Code and CodeModel properties of an entity.

### Key components

* **```DagGenerator```**: This class is the foundation of the project. It parses RETW files, extracts entities and mappings, and constructs the DAG. Key methods include ```add_RETW_file``` (adds a single RETW file), ```get_dag_total``` (returns the overall DAG), ```get_dag_ETL``` (returns the ETL flow DAG), and methods for retrieving specific subgraphs.

* **```DagReporting```**: This class leverages the DAG created by ```DagGenerator``` to provide insights and visualizations. It offers methods like ```get_mapping_order``` (determines the execution order), ```plot_graph_total``` (visualizes the entire DAG), ```plot_etl_dag``` (visualizes the ETL flow), and methods for visualizing dependencies and entity relationships.

* **```EtlFailure```**: This class simulates and analyzes the impact of ETL job failures. It uses set_pd_objects_failed to specify failing components and ```get_report_fallout``` and ```plot_etl_fallout``` to report and visualize the consequences.

* **```EntityRef```** and **```MappingRef```**: These namedtuples represent entities and mappings, respectively, providing a structured way to reference them within the DAG.

* **```VertexType```** and **```EdgeType```**: These enums define the types of nodes and edges in the DAG, improving code clarity and maintainability.

The project uses a graph-based approach to represent and analyze ETL dependencies, providing valuable insights for understanding and optimizing the ETL process. The ```DagGenerator``` builds the DAG, ```DagReporting``` provides analysis and visualization, and ```EtlFailure``` simulates failure scenarios.

### Classes diagram

In this section I describe the classes, what they are used for and how they fit together.

```mermaid
---
  config:
    class:
      hideEmptyMembersBox: true
---
classDiagram
  DagGenerator <|-- DagReporting
  DagReporting <|-- EtlFailure
  DagGenerator *-- EdgeType
  DagGenerator *-- VertexType
  EntityRef --> DagGenerator
  MappingRef --> DagGenerator

  class EntityRef{
    <<namedtuple>>
    CodeModel
    CodeEntity
  }
  class MappingRef{
    <<namedtuple>>
    FileRETW
    CodeMapping
  }
  class VertexType{
    <<enumeration>>
    ENTITY
    MAPPING
    FILE
    ERROR
  }
  class EdgeType{
    <<enumeration>>
    FILE_ENTITY
    FILE_MAPPING
    ENTITY_SOURCE
    ENTITY_TARGET
  }
  class DagGenerator{
    +add_RETW_files(list files_RETW)
    +add_RETW_file(str file_RETW)
    +get_dag_total()
    +get_dag_single_retw_file(str file_RETW)
    +get_dag_file_dependencies(bool include_entities)
    +get_dag_entity(EntityRef entity)
    +get_dag_ETL()
  }
  class DagReporting{
    +get_mapping_order() list
    +plot_graph_total(str file_html)
    +plot_graph_retw_file(str file_retw, str file_html)
    +plot_file_dependencies(str file_html, bool include_entities)
    +plot_entity_journey(EntityRef entity, str file_html)
    +plot_etl_dag(str file_html)
  }
  class EtlFailure{
    +set_pd_objects_failed(list)
    +get_report_fallout() list
    +plot_etl_fallout(str file_html)
  }
```
