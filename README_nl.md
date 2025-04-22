# Mapping dependency parser

Dit project analyseert afhankelijkheden in een ETL-proces (Extract, Transform, Load) dat is gedefinieerd door RETW-bestanden. Het helpt bij het bepalen van de optimale uitvoeringsvolgorde van mappings, identificeert potentiële fouten en visualiseert de afhankelijkheden tussen entiteiten en bestanden. De kernfunctionaliteit draait om het bouwen van een gerichte acyclische graaf (DAG) die de ETL-flow voorstelt.

Het dekt globaal het volgende:

* wat de [volgorde van mappings](#bepalen-van-mapping-volgorde) zou moeten zijn in de ETL-flow, en of de ETL-flow geen gesloten lussen bevat (ETL-flows moeten [acyclisch](https://nl.wikipedia.org/wiki/Gerichte_acyclische_graaf) zijn),
* het vinden van verwijzingen naar entiteiten die niet gedefinieerd zijn in de verwerkte RETW-bestanden,
* de gevolgen van een fout in een stap van het ETL-proces en
* de afhankelijkheden tussen RETW-bestanden voor entiteiten.

## Voorbeeld uitvoeren

De map ```dependency_checker``` bevat een bestand ```example.py``` dat laat zien hoe alle klassen gebruikt kunnen worden voor bovenstaande doeleinden.

Het voorbeeld verwijst naar een lijst van voorbeeld-RETW-bestanden die geplaatst zijn in de submap ```retw_examples```. De volgorde van de bestanden in de lijst is niet relevant voor de functionaliteit, dus je kunt eigen bestanden in willekeurige volgorde aan de lijst toevoegen.

Er wordt gebruik gemaakt van de klasse ```DagReporting```, gedefinieerd in het bestand ```dag_reporting.py```, om visualisaties te maken van:

* het totale netwerk van bestanden, entiteiten en mappings,
* het netwerk van verbonden bestanden, entiteiten en mappings van een specifieke entiteit,
* afhankelijkheden tussen bestanden, gebaseerd op gedeelde entiteiten, en
* een visualisatie van de ETL-flow voor alle gecombineerde RETW-bestanden.

Daarnaast worden bestanden gegenereerd met:

* de volgorde van mappings in een ETL-flow en
* de entiteiten die gebruikt worden in mappings, maar geen definitie hebben in één van de bestanden.

De klasse ```EtlFailure```, gedefinieerd in het bestand ```dag_etl_failure.py```, wordt gebruikt om:

* een visualisatie te maken van de gevolgen van een falend ETL-flow object en
* een rapportage te maken van de falende ETL-flow objecten.

## Implementatiedocumentatie

### Bepalen van mapping volgorde

De uitvoeringsvolgorde van mappings wordt bepaald door twee componenten:

* Run level: waar in de Directed Acyclic Graph ([DAG](https://nl.wikipedia.org/wiki/Gerichte_acyclische_graaf)) hiërarchie, gaande van bron-entiteiten naar eind-entiteiten, de mapping zich bevindt. Mappings die enkel bron-entiteiten gebruiken krijgen run level 0, de volgende run levels worden bepaald door het aantal mappings dat in de hiërarchie vóór de huidige mapping komt.
* Run level stage: Als mappings op hetzelfde run level dezelfde entiteiten gebruiken, moeten ze een verschillende uitvoeringsvolgorde krijgen om deadlocks te voorkomen. Een [greedy coloring algoritme](https://www.youtube.com/watch?v=vGjsi8NIpSE) wordt gebruikt om de uitvoeringsvolgorde binnen een run level te bepalen.

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

### Bouwen van de ETL DAG

De mapping dependency parser gebruikt [grafen](https://nl.wikipedia.org/wiki/Graaf_(wiskunde)), meer specifiek een [DAG](https://nl.wikipedia.org/wiki/Gerichte_acyclische_graaf), wat een netwerkvoorstelling is van de bestanden, entiteiten (bijv. tabellen) en mappings. Deze sectie legt uit hoe de DAG gecreëerd wordt.

Voor elk RETW-bestand worden de mappings geëxtraheerd, en de mappings, bron- en doel-entiteiten worden omgezet naar knopen (ook wel vertices genoemd). Vervolgens worden er verbindingen (ook wel edges genoemd) gelegd tussen de bron-entiteiten en de mappings en tussen de mappings en de doel-entiteiten. Als alle mappings zijn omgezet in knopen en verbindingen, kunnen deze gecombineerd worden tot een netwerk. Deze netwerkvoorstelling maakt de berekeningen mogelijk die in de introductie zijn beschreven.

```mermaid
erDiagram
ENTITY ||--|{ MAPPING: "Gevuld door: ENTITY_TARGET"
MAPPING ||--|{ ENTITY: "Gebruikt: ENTITY_SOURCE"
FILE_RETW ||--o{ MAPPING: "Bevat: FILE_MAPPING"
FILE_RETW ||--o{ ENTITY: "Bevat: FILE_ENTITY"
```

In een Power Designer-document (en het corresponderende RETW-bestand) worden alle objecten geïdentificeerd door hun 'Id'-attribuut, dat er bijvoorbeeld uitziet als 'o123'. Deze Id is intern geldig binnen een document, maar niet geschikt om objecten te identificeren wanneer we de resultaten van meerdere Power Designer-documenten combineren. Daarom moeten er nieuwe identifiers aangemaakt worden zodat er geen conflicten ontstaan tussen documenten, en tegelijkertijd de integriteit behouden blijft (bijvoorbeeld als een doel-entiteit van het ene document een bron is in een mapping van een ander document). Hoe wordt dit bereikt?

* We gaan ervan uit dat mappings uniek zijn tussen Power Designer-documenten. Om een unieke mapping-ID te maken, wordt een hash toegepast op de combinatie van de RETW-bestandsnaam en de mapping-code.

* Voor consistente identificatie van entiteiten over documenten heen, wordt een hash toegepast op de combinatie van de Code- en CodeModel-eigenschappen van een entiteit.

### Belangrijke componenten

* **```DagGenerator```**: Deze klasse vormt de basis van het project. Het parseert RETW-bestanden, extraheert entiteiten en mappings, en bouwt de DAG. Belangrijke methoden zijn ```add_RETW_file``` (voegt een RETW-bestand toe), ```get_dag_total``` (geeft de totale DAG terug), ```get_dag_ETL``` (geeft de ETL-flow DAG terug), en andere methoden om specifieke subgrafen op te halen.

* **```DagReporting```**: Deze klasse gebruikt de DAG van ```DagGenerator``` om inzichten en visualisaties te leveren. Methoden zijn onder andere ```get_mapping_order``` (bepaalt de uitvoeringsvolgorde), ```plot_graph_total``` (visualiseert de totale DAG), ```plot_etl_dag``` (visualiseert de ETL-flow), en andere methoden om afhankelijkheden en relaties weer te geven.

* **```EtlFailure```**: Deze klasse simuleert en analyseert de impact van falende ETL-jobs. De methode ```set_entities_failed``` specificeert de falende componenten, en ```get_report_fallout``` en ```plot_etl_fallout``` leveren rapportages en visualisaties van de gevolgen.

* **```EntityRef```** en **```MappingRef```**: Deze namedtuples representeren respectievelijk entiteiten en mappings, en geven een gestructureerde manier om ze in de DAG te refereren.

* **```VertexType```** en **```EdgeType```**: Deze enums definiëren de typen knopen en verbindingen in de DAG, wat bijdraagt aan duidelijkheid en onderhoudbaarheid van de code.

Het project gebruikt een graaf-gebaseerde aanpak om ETL-afhankelijkheden te representeren en analyseren, en biedt waardevolle inzichten voor het begrijpen en optimaliseren van het ETL-proces. ```DagGenerator``` bouwt de DAG, ```DagReporting``` verzorgt analyse en visualisatie, en ```EtlFailure``` simuleert foutscenario's.

### Klassen diagram

In deze sectie worden de klassen beschreven, waarvoor ze gebruikt worden en hoe ze samenhangen.

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