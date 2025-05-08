# DevOps

## Overzicht

Dit bestand definieert automatisering voor interactie met Azure DevOps Git-repositories als onderdeel van een data-engineeringworkflow. Het doel is om het proces van het klonen van een repository, het aanmaken van een feature-branch, het genereren van DDL/ETL-bestanden en het publiceren van wijzigingen terug naar de repository te stroomlijnen. De configuratie wordt gelezen uit een YAML-bestand en de automatisering is opgezet als een zelfstandig uitvoerbare script.

### Rol in het Grotere Systeem

Deze module fungeert als een automatiserings- en integratielaag tussen de DevOps-repository en het data-engineeringsysteem. Het zorgt ervoor dat codegeneratie en publicatie consistent en herhaalbaar worden uitgevoerd, met een focus op versiebeheer en traceerbaarheid. Dit vereenvoudigt het beheer van ETL- en DDL-bestanden in een gestructureerde DevOps-omgeving.

## Externe Afhankelijkheden

* **Generator en Publisher:**

  * `DDLGenerator` en `DDLPublisher` zijn geïmporteerde modules die verantwoordelijk zijn voor het genereren en publiceren van DDL/ETL-bestanden.

* **Systeemtools:**

  * [`Git`](https://git-scm.com/): Voor het klonen en beheren van de repository.
  * [`Webbrowser`](https://docs.python.org/3/library/webbrowser.html): Voor het openen van de DevOps-pagina voor pull requests.

## Belangrijkste Componenten

### DevOpsHandler (klasse)

* **Doel:** Beheert de DevOps-activiteiten, inclusief het klonen van repositories, het aanmaken van feature-branches en het publiceren van wijzigingen.
* **Initialisatie:**

  * Neemt een configuratiedictionary aan met DevOps-specifieke parameters zoals repository-URL, branchnaam en authenticatiegegevens.

**Methoden:**

* `get_repo()`

  * Rol: Clone de repository en maak een nieuwe feature-branch aan.
  * Werking:

    * Controleert of de repository al bestaat.
    * Kloneert de repository naar een lokale map.
    * Wisselt naar de opgegeven feature-branch.

* `publish_repo()`

  * Rol: Commit en push wijzigingen naar de DevOps-repository.
  * Werking:

    * Voegt nieuwe of gewijzigde bestanden toe aan de commit.
    * Voert een commit uit met een gegenereerd of opgegeven commit-bericht.
    * Pusht de commit naar de feature-branch in de remote repository.
    * Opent de DevOps-webpagina van de repository in een webbrowser voor een pull request (indien nodig).

---

### Uitvoeringsstroom als Script

Wanneer het script rechtstreeks wordt uitgevoerd (`__main__` sectie):

1. **Configuratie laden:**

   * Laadt configuratie-instellingen uit `etl_templates/config.yml`.
   * Haalt repository-URL, branchnaam, en bestandslocaties op.

2. **Repositorybeheer:**

   * Instantieert `DevOpsHandler` met de configuratieparameters.
   * Voert `get_repo()` uit om de repository te klonen en de feature-branch aan te maken.

3. **Bestandsgeneratie:**

   * Roept de `DDLGenerator` en `DDLPublisher` aan om DDL/ETL-bestanden te genereren en lokaal op te slaan.

4. **Publicatie:**

   * Voert `publish_repo()` uit om de gegenereerde bestanden te committen en te pushen naar de DevOps-repository.
