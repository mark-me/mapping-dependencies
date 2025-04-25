# Genesis Orkestratie

Het script ```main.py``` is het startpunt van de MMDE pijplijn genaamd Genesis. Deze pijplijn leest configuratie uit een YAML-bestand, verwerkt Power Designer-modelbestanden, controleert afhankelijkheden en genereert uitrolcode voor deployment.

## Gebruik

* Zorg dat alle PowerDesigner-bestanden op de juiste locatie staan.
* Vul een YAML-configuratiebestand in op basis van het sjabloon ([zie voorbeeld](#voorbeeld-configuratiebestand)).
* Start het script met het pad naar het configuratiebestand:

```bash
python main.py path/to/config.yaml
```

## Verwerkingsvolgorde van Genesis

```mermaid
sequenceDiagram
  participant G as Genesis
  participant CF as Configuratiebestand
  participant PD as PowerDesigner-bestand
  participant E as Extractor
  participant D as Afhankelijkheidschecker
  participant DG as Codegenerator

  G->CF: Leest configuratie
  loop Voor elk PowerDesigner-bestand
    G->E: extract(PD)
    E->PD: Leest gegevens
    E-->G: Geeft geëxtraheerde data terug
  end
  G->D: check_dependencies(geëxtraheerde data)
  D->D: Controleert afhankelijkheden
  D-->G: Retourneert eventuele problemen
  alt Geen problemen
    G->DG: generate_deployment(geëxtraheerde data)
    DG->DG: Genereert uitrolcode
  else Problemen gevonden
    G->G: Schrijft problemen weg naar bestand
    G->G: Stopt uitvoering
  end
```

## Class-diagram

```mermaid
classDiagram
    Genesis -- ConfigFile : gebruikt
    ConfigFile -- ConfigData : bevat
    ConfigData o-- PowerDesignerConfig
    ConfigData o-- ExtractorConfig
    ConfigData o-- GeneratorConfig
    ConfigData o-- PublisherConfig
    ConfigData o-- DevOpsConfig
```

## Configuratiegegevens

De configuratie wordt opgeslagen in dataclasses die zijn afgeleid van de YAML-structuur. Deze bieden typeveiligheid en automatische validatie.

### Voorbeeld configuratiebestand

```yaml
# Titel van het project of run
title: "voorbeeld-run"

# Hoofdmap waarin alle tussenbestanden en output worden opgeslagen
folder_intermediate_root: "/pad/naar/intermediate"

# Instellingen voor PowerDesigner-modellen
power-designer:
  # Submap waar PowerDesigner-bestanden zich bevinden
  folder: "PowerDesigner"
  # Lijst met LDM-bestanden die geanalyseerd moeten worden
  files:
    - "model1.ldm"
    - "model2.ldm"

# Extractor-instellingen
extractor:
  # Submap waar geëxtraheerde gegevens (RETW-bestanden) worden opgeslagen
  folder: "RETW"

# Generator-instellingen
generator:
  # Submap waar gegenereerde output wordt opgeslagen
  folder: "generator"
  # Platformconfiguratie voor templates (bijv. "dedicated-pool" of "shared")
  templates_platform: "dedicated-pool"
  # Naam van JSON-bestand waarin gemaakte DDL-bestanden worden geregistreerd
  created_ddls_json: "list_created_ddls.json"

# Publisher-instellingen
publisher:
  # Pad naar de Visual Studio-projectmap
  vs_project_folder: "VSProject"
  # Pad naar het .sqlproj-bestand binnen het project
  vs_project_file: "./CentralLayer/project.sqlproj"
  # JSON-bestand met een lijst van codelijsten
  codeList_json: "./output/codeList.json"
  # Map waarin codelijsten als input worden verwacht
  codeList_folder: "./input/codeList/"
  # Map met MDDE scripts voor deployment
  mdde_scripts_folder: "./src/mdde_scripts/"

# DevOps-integratie-instellingen
devops:
  # Naam van de Azure DevOps organisatie
  organisation: "organisatie-naam"
  # Naam van het project in Azure DevOps
  project: "project-naam"
  # Repository waarin wijzigingen worden gepusht
  repo: "repository-naam"
  # Naam van de branch waarop gewerkt wordt
  branch: "feature-branch"
  # Werkitem-ID dat gekoppeld wordt aan deze deployment
  work_item: "12345"
  # Omschrijving van het werkitem of de deployment
  work_item_description: "Beschrijving van deze automatische deployment"
```

### Belangrijke componenten

**```ConfigData```**: Bevat globale instellingen zoals de titel van het project en het pad naar de outputmap.

**```PowerDesignerConfig```**: Bevat de map en bestanden van PowerDesigner.

**```ExtractorConfig```**: Map voor geëxtraheerde RETW-bestanden.

**```GeneratorConfig```**: Bevat configuratie voor de Generator, inclusief platformtemplates, een JSON-bestand met aangemaakte DDL’s en de uitvoermap.

**```PublisherConfig```**: Bevat instellingen voor de Publisher, zoals paden naar Visual Studio-projecten, codelijsten en MDDE-scripts.

**```DevOpsConfig```**: Bevat informatie met betrekking tot DevOps-integratie, waaronder organisatie, project, repository, branch en details van het werkitem.

## API referentie

### Class-diagram met details

```mermaid
classDiagram
    class Genesis {
    +__init__(file_config: str)
    +extract(file_pd_ldm: Path) : str
    +check_dependencies(files_RETW: list) : None
    +generate_deployment(files_RETW: list) : None
    +clone_repository() : str
    +start_processing()
    }
    class ConfigFile {
        +__init__(file_config: str)
        +example_config(file_output: str) : None
        +dir_intermediate : str
        +files_power_designer : list
        +dir_extract : str
        +dir_generate : str
        +devops_config : DevOpsConfig
    }
    class PowerDesignerConfig{
        +folder: str
        +files: List[str]
    }
    class ExtractorConfig{
        +folder: str
    }
    class GeneratorConfig{
        +templates_platform: str
        +created_ddls_json: str
        +folder: str
    }
    class PublisherConfig{
        +vs_project_folder: str
        +vs_project_file: str
        +codeList_json: str
        +codeList_folder: str
        +mdde_scripts_folder: str
    }
    class DevOpsConfig{
        +organisation: str
        +project: str
        +repo: str
        +branch: str
        +work_item: str
        +work_item_description: str
    }
    class ConfigData{
        +title: str
        +folder_intermediate_root: str
        +power_designer: PowerDesignerConfig
        +extractor: ExtractorConfig
        +generator: GeneratorConfig
        +publisher: PublisherConfig
        +devops: DevOpsConfig
    }

    Genesis -- ConfigFile : uses
    ConfigFile -- ConfigData : has a
    ConfigFile -- DevOpsConfig : has a
    ConfigData o-- PowerDesignerConfig : has
    ConfigData o-- ExtractorConfig : has
    ConfigData o-- GeneratorConfig : has
    ConfigData o-- PublisherConfig : has
    ConfigData o-- DevOpsConfig : has
```
