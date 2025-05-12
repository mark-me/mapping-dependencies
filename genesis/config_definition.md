# Configuratie Data

## Overzicht

Dit bestand definieert het configuratieschema voor Genesis. Het maakt gebruik van Python [`dataclasses`](https://www.dataquest.io/blog/how-to-use-python-data-classes/) om configuratie-opties voor verschillende subsystemen te structureren en documenteren, zoals PowerDesigner-integratie, data-extractie, codegeneratie, publicatie en DevOps-workflows.

Het bestand fungeert als een centrale plaats om alle configuratiegegevens die door de applicatie worden vereist, te definiëren, valideren en beheren.

---

## Belangrijkste Componenten

### ConfigData

* **Doel:**
  * De hoofdconfiguratieklasse die alle bovenstaande configuraties groepeert.

* **Velden:**

  * `application_title`: Titel van de applicatie (bijv. "Data Pipeline Generator").
  * `root_folder`: Root-directory voor alle gegenereerde bestanden.
  * `power_designer`: Instantie van [`PowerDesignerConfig`](#powerdesignerconfig).
  * `extractor`: Instantie van [`ExtractorConfig`](#extractorconfig).
  * `generator`: Instantie van [`GeneratorConfig`](#generatorconfig).
  * `publisher`: Instantie van [`PublisherConfig`](#publisherconfig).
  * `devops`: Instantie van [`DevOpsConfig`](#devopsconfig).

---

### PowerDesignerConfig

* **Doel:**

  * Omvat de configuratie voor de integratie met PowerDesigner.
* **Velden:**

  * `folder`: Pad naar de PowerDesigner-bestanden.
  * `file_names`: Lijst met relevante bestandsnamen voor verwerking.

---

### ExtractorConfig

* **Doel:**

  * Bevat instellingen voor het data-extractiecomponent.
* **Velden:**

  * `output_folder`: Pad naar de extractiedirectory waar de gegenereerde data wordt opgeslagen.

---

### GeneratorConfig

* **Doel:**

  * Bevat configuratie voor de code- of DDL-generator.
* **Velden:**

  * `template_folder`: Pad naar de Jinja2 SQL templates.
  * `output_folder`: Pad naar de directory voor gegenereerde DDL- en ETL-bestanden.
  * `json_created_ddls`: Pad naar een JSON-bestand dat alle gegenereerde DDL-bestanden opsomt.

---

### PublisherConfig

* **Doel:**

  * Beheert instellingen voor het publicatieproces.
* **Velden:**

  * `project_file`: Pad naar het Visual Studio projectbestand (`.sqlproj`).
  * `code_list_folder`: Pad naar de directory met code-lijsten (bijv. referentiedata).
  * `script_folder`: Pad naar de folder met gegenereerde scripts.

---

### DevOpsConfig

* **Doel:**

  * Definieert parameters voor DevOps-integratie.
* **Velden:**

  * `organization`: Naam van de DevOps-organisatie.
  * `project`: Naam van het DevOps-project.
  * `repository`: Reponame in DevOps.
  * `branch`: Standaard branch voor feature development.
  * `work_item`: Optioneel veld voor werkitem ID's, gekoppeld aan de wijzigingen.

---

## Voorbeeldconfiguratie in YAML

```yaml
application_title: "Data Pipeline Generator"
root_folder: "/path/to/project"

power_designer:
  folder: "/path/to/powerdesigner/files"
  file_names:
    - model1.pdm
    - model2.pdm

extractor:
  output_folder: "/path/to/extracted/data"

generator:
  template_folder: "/path/to/templates"
  output_folder: "/path/to/generated/ddl"
  json_created_ddls: "/path/to/generated/ddl/created_ddls.json"

publisher:
  project_file: "/path/to/vs/project.sqlproj"
  code_list_folder: "/path/to/code/lists"
  script_folder: "/path/to/scripts"

devops:
  organization: "MyOrg"
  project: "DataProject"
  repository: "DataRepo"
  branch: "main"
  work_item: 1234
```

---

## Voordelen van Gebruik van Dataclasses

* **Typeveiligheid:** Voorkomt typefouten en zorgt voor consistente toegang tot configuratievelden.
* **Standaardwaarden:** Vergemakkelijkt het gebruik van standaardwaarden voor ontbrekende configuratievelden.
* **Documentatie:** Elke `dataclass` bevat een docstring die automatisch gegenereerd kan worden voor API-documentatie.
* **Conversie naar Dict:** Maakt het eenvoudig om configuratiegegevens om te zetten naar JSON/YAML voor opslag of verdere verwerking.

---

## Gebruik in de Applicatie

* **Initialisatie:** De configuratie wordt ingelezen vanuit een YAML-bestand en gemapt naar een `ConfigData` object.

* **Toegang tot Velden:** De configuratie wordt doorgegeven aan andere componenten, bijvoorbeeld:

  ```python
  config = ConfigData.load_from_yaml("config.yml")
  generator_path = config.generator.output_folder
  ```

* **Validatie:** Tijdens het laden worden verplichte velden gecontroleerd en ontbrekende waarden aangevuld met standaardwaarden.

* **Logging:** Foutmeldingen of ontbrekende configuratievelden worden gelogd voor eenvoudige debugging.

---

## Conclusie

Dit bestand definieert een robuust en gestructureerd configuratieschema voor de applicatie, waarbij dataclasses worden gebruikt voor typeveiligheid, standaardwaarden en documentatie. De `ConfigData` klasse fungeert als de centrale toegangspoort voor configuratiegegevens, wat zorgt voor consistente verwerking en eenvoudige integratie met andere modules. De integratie van DevOps-parameters maakt het schema compleet voor data-extractie, -generatie, -publicatie en -automatisering in een DevOps-context.
