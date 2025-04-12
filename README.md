# Mapping dependency parser

Builds insights in the network of entities and mappings, by using RETW ouput files, to determine:

* what the [ordering of mappings](#mapping-order) should be in the ETL flow, and whether the ETL flow has no closed loops (ETL-flows should be [acyclic](https://en.wikipedia.org/wiki/Directed_acyclic_graph)),
* the [consequences of a failure](#etl-job-failures) of a step in ETL process and
* the [dependencies between RETW files](#document-dependencies) for entities.

## Mapping order

The ordering of mappings can be determined using ```mapping_order.py``` and changing the list with filenames in the ```main``` function's variable ```lst_files_RETW```. This script also checks whether the ETL flow is acyclic.

### Determining the order

The running order of mappings is determined by two components:

* Run level: where in the DAG hierarchy, going from source entities to end entities, is the mapping positioned. The mappings taking in only source entities are set at run level 0, the next run levels are determined by the number of mappings in the hierarchy running before the mapping under consideration.
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

### Output mapping order

Output generated by this script can be found in the files:

* ```output/dag_structure_*.html``` shows the structure of the ETL, and
* ```output/mapping_order_*.jsonl``` that contains the ordering of the mapping executing, which can be adopted by the orchestrator.

The asterisks in the filename indicates the iteration of each RETW file added to the network. This iterative output enables troubleshooting.

## Document dependencies

Since a whole ETL flow can be split across different Power Designer documents, there will also be multiple RETW files. Entities created in one document can be used as a source for a mapping in another Power Designer document.

The python file ```graph_retw_files.py``` contains the functionalities to see what the file depencencies are and how entities 'travel' across different files.

### File dependencies

RETW files can be connected because an entity created in one file can be used in the mapping of another file. The function ```plot_graph_total``` of the class ```GraphRETWFiles```.

### Entity journey

The function ```plot_entity_journey``` of the class ```GraphRETWFiles``` creates a HTML file that shows all the files, entities and mappings that are related to the entity in question.

An example of the function in action can be found in the main function where the model and entity is supplied:

```py
graph.plot_entity_journey(
        code_model="Da_Central_CL",
        code_entity="DmsProcedure",
        file_html="output/entity_journey.html",
    )
```

## ETL job failures

A simulation a failing ETL process can be simulated using ```etl_failure_simulator.py```. The list with filenames in the ```main``` function's variable ```lst_files_RETW``` can be adjusted. In the same function you can 'simulate' an ETL-step failure by adjusting the list ```lst_id_entities_failed```; although the variable name suggests only entities can fail, you can also set this ID to a mapping.

### Output job failures

Output generated by this script can be found in the files:

* ```output/dag_run_report.html``` that contains a graphical representation of the failure consequences and
* ```output/dag_run_fallout.json``` that contains a reports on the mappings/entities affected by the failure.

## Building the ETL DAG

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

* We assume mappings are unique across Power Designer documents. To build a mapping identifier a hash is applied to the combination of the RETW filename and the mapping object ID.
* To maintain consistency identification of entities across Power Designer documents a hash is applied to the combination of the Code and CodeModel properties of an entity.

### Classes and uses

In this section I describe the classes, what they are used for and how they fit together.

```mermaid
---
  config:
    class:
      hideEmptyMembersBox: true
---
classDiagram
  GraphRETWBase <|-- GraphRETWFiles
  GraphRETWFiles <|-- DagETL
  DagETL <|-- ETLFailureSimulator
  GraphRETWBase *-- EdgeType
  GraphRETWBase *-- VertexType

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
  class GraphRETWBase{
    <<Abstract>>
  }
  class GraphRETWFiles{
    +add_RETW_files(list)
    +add_RETW_file(str)
    +plot_graph_total(str)
    +plot_graph_retw_file(str)
    +plot_file_dependencies(str)
    +plot_entity_journey(str)
  }
  class DagETL{
    +get_mapping_order() list
    +plot_dag(str)
  }
  class ETLFailureSimulator{
    +set_entities_failed(list)
    +get_report_fallout() dict
    +plot_dag_fallout(str)
  }
```
