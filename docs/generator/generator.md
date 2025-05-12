# Generator

## Overzicht

Dit bestand definieert een Python-module voor het genereren van DDL (Data Definition Language) en ETL (Extract, Transform, Load) scripts uit een JSON-model, dat wordt gegenereerd de Extractor. De module bevat de centrale klasse `DDLGenerator`, die het proces orkestreert van het lezen van configuratie- en modelbestanden, het toepassen van Jinja2 SQL-templates en het schrijven van de resulterende SQL-scripts en metadata naar een Visual Studio-projectstructuur. De generator ondersteunt platformspecifieke templates en houdt een logboek bij van alle gegenereerde bestanden voor verdere publicatie- of implementatiestappen.

---

### Rol in het Grotere Systeem

De `DDLGenerator`-klasse fungeert als een centrale component voor de vertaling van JSON-modeldata naar database-artefacten, met name voor ETL- en DDL-processen. Het maakt gebruik van templates om platform-specifieke SQL-scripts te genereren en zorgt ervoor dat gegenereerde artefacten worden gedocumenteerd voor latere verwerking in DevOps-pijplijnen.

Deze aanpak ondersteunt:

* **Consistentie:** Templates zorgen voor gestandaardiseerde SQL-scripts.
* **Herbruikbaarheid:** Door gebruik van Jinja2-templates kunnen aanpassingen centraal worden beheerd.
* **Traceerbaarheid:** De gegenereerde JSON-output biedt een log van alle bestanden, inclusief hun locatie en implementatiestatus.

---

### Outputbeheer

* De gegenereerde DDL- en ETL-bestanden worden georganiseerd in submappen per entiteit, view of post-deployment script.
* Een JSON-bestand (`generated_ddls.json`) biedt een overzicht van alle gegenereerde bestanden, gecategoriseerd per type.

---

## Afhankelijkheden

* **[Jinja2](https://jinja.palletsprojects.com/en/stable/):** Voor het renderen van SQL-templates.
* **[sqlparse/sqlfluff](https://sqlfluff.com/):** Voor het formatteren en linten van gegenereerde SQL-scripts.
* **[Pathlib](https://docs.python.org/3/library/pathlib.html):** Voor platformonafhankelijke padbeheer.
* **YAML/JSON:** Voor configuratie en uitvoer.

## Belangrijkste Componenten

### DDLGenerator (klasse)

* **Doel:** Verantwoordelijk voor het volledige proces van het genereren van DDL- en ETL-scripts uit een JSON-model.
* **Initialisatie:**

  * Neemt een dictionary van parameters aan, zoals paden, template-informatie en uitvoerlocaties.
  * Initieert de interne status, waaronder een uitvoervolgregistratie (`dict_created_ddls`).

---

### Belangrijke Methoden

* `read_model_file()`

  * Laadt het JSON-modelbestand en converteert het naar een Python-dictionary voor verdere verwerking.

* `get_templates()`

  * Laadt Jinja2 SQL-templates uit de opgegeven template-map.
  * Templates zijn per platform gestructureerd, bijvoorbeeld voor SQL Server of PostgreSQL.

* `write_ddl()`

  * Hoofdmethodiek die het proces van DDL/ETL-generatie triggert.
  * Roept specifieke methoden aan voor entiteiten, source views en post-deployment scripts.

* `write_json_created_ddls()`

  * Schrijft een JSON-bestand met een overzicht van alle gegenereerde DDL/ETL-bestanden.
  * Dit bestand kan door andere componenten worden gebruikt om gegenereerde artefacten te publiceren of te implementeren.

---

### Interne Hulpmethoden

* `__copy_mdde_scripts()`

  * Kopieert MDDE-scripts naar de projectrepository.
  * Houdt bij welke bestanden zijn gekopieerd voor traceerbaarheid.

* `__select_identifiers()`

  * Extraheert en verwerkt identifier-informatie (bijv. primary keys, business keys) uit het model.
  * Wordt gebruikt bij het genereren van hash keys in views.

* `__write_ddl_entity()`

  * Genereert DDL-scripts voor database-entiteiten (tabellen).
  * Verwerkt attributen en identifiers volgens platform-specifieke SQL-templates.

* `__write_ddl_sourceview_aggr()`

  * Genereert ETL-source views voor aggregaten en business rules.
  * Implementeert logica voor het samenvoegen en aggregeren van gegevens.

* `__write_ddl_sourceview()`

  * Genereert ETL-source views voor reguliere entiteiten.
  * Voegt hash key-calculaties en attributenmapping toe.

* `__write_ddl_MDDE_PostDeploy_Config()`

  * Creëert post-deployment scripts voor configuratiemetadata.
  * Beheert master scripts en implementatievolgorde.

* `__write_ddl_MDDE_PostDeploy_CodeTable()`

  * Genereert post-deployment scripts voor code tabellen.
  * Implementeert logica voor codelijsten en referentietabellen.

---

## Uitvoeringsstroom als Script

Wanneer het script rechtstreeks wordt uitgevoerd (`__main__` sectie):

1. **Configuratie Laden:**

   * Laadt configuratieparameters uit `etl_templates/config.yml`.
   * Haalt model- en templatepaden, uitvoerlocaties en DevOps-parameters op.

2. **Parameter Voorbereiding:**

   * Maakt parameterdictionaries voor de generator aan, inclusief paden naar templates en uitvoermappen.

3. **Generatie Starten:**

   * Instantieert `DDLGenerator`.
   * Laadt het modelbestand en templates.
   * Start het generatieproces voor DDL- en ETL-scripts.

4. **JSON Output Genereren:**

   * Schrijft een JSON-bestand met een overzicht van alle gegenereerde bestanden (`generated_ddls.json`).
