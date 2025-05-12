# ConfigFile

## Overzicht

Dit bestand definieert de `ConfigFile` klasse, die verantwoordelijk is voor het beheren van applicatieconfiguratie via een YAML-bestand. Het biedt mechanismen om configuratiegegevens te lezen, valideren en schrijven, evenals om toegang te bieden tot verschillende paden en bestanden die door de applicatie worden gebruikt. De configuratiestructuur is opgezet met behulp van `dataclasses`, waardoor validatie, standaardwaarden en typecontrole zijn ingebouwd. Daarnaast ondersteunt de klasse het genereren van voorbeeldconfiguratiebestanden met nuttige opmerkingen.

Het bestand speelt een centrale rol in het configuratiebeheer van de applicatie en fungeert als de interface tussen het YAML-configuratiebestand en de rest van het systeem. Het behandelt foutafhandeling, aanmaak van directories en biedt eenvoudige toegang tot configuratiegestuurde paden en instellingen.

---

## Belangrijkste Componenten

### ConfigFileError (Exception)

* **Doel:**

  * Een aangepaste uitzondering voor configuratiebestandsfouten, met een foutcode voor fijnmazige foutafhandeling.

---

### ConfigFile (Klasse)

* **Doel:**

  * De hoofdklasse voor het beheren van configuratie.
  * Leest configuratie uit een YAML-bestand, valideert verplichte velden en vult standaardwaarden in.
  * Biedt eigenschappen voor toegang tot belangrijke directories en bestanden (bijv. tussenresultaten, PowerDesigner-bestanden, extractie- en generatiebestanden).
  * Ondersteunt versiebeheer voor uitvoermappen door versienummers te verhogen op basis van bestaande directories.
  * Kan een voorbeeldconfiguratiebestand genereren met inline opmerkingen voor gebruikersbegeleiding.

---

#### Belangrijkste Methoden

##### \_read\_file()

* Leest het YAML-configuratiebestand en zet de inhoud om in de juiste `dataclass`-structuur.
* Controleert verplichte velden en logt ontbrekende of ongeldige configuratie-opties.

---

##### **\_fill\_defaults()**

* Recursieve methode die standaardwaarden invult voor `dataclass`-velden.
* Ondersteunt geneste `dataclasses` en standaardfactories.

---

##### **\_create\_dir()**

* Zorgt ervoor dat vereiste directories bestaan, en maakt ze aan indien nodig.
* Logt een waarschuwing bij problemen met het aanmaken van directories.

---

##### **\_determine\_version()**

* Bepaalt het volgende versienummer voor uitvoermappen door bestaande directories te inspecteren en het patchnummer te verhogen.
* Formaat: `v1.0.0`, `v1.0.1`, enz.

---

##### **\_config\_to\_yaml\_with\_comments()**

* Zet een configuratie `dataclass` om naar een YAML-string met opmerkingen bij elk veld.
* Helpt gebruikers bij het begrijpen van de configuratie-opties.

---

##### **example\_config()**

* Genereert een voorbeeldconfiguratiebestand met standaardwaarden en verklarende opmerkingen.
* Maakt gebruik van `_config_to_yaml_with_comments()` voor consistente opmaak.

---

#### **Eigenschappen**

De klasse biedt diverse eigenschappen voor eenvoudige toegang tot configuratiegestuurde paden:

* **`dir_intermediate`**: Pad naar de directory voor tussenresultaten.
* **`files_power_designer`**: Lijst van PowerDesigner-bestanden.
* **`dir_extract`**: Pad naar de extractiedirectory.
* **`dir_generate`**: Pad naar de generatiedirectory.
* **`devops_config`**: DevOps-specifieke configuratie-instellingen.

---

### Integratie met Andere Modules

* **ConfigData en DevOpsConfig:**

  * Geïmporteerd uit het `config_definition`-bestand.
  * Structureren configuratiegegevens met `dataclasses`, inclusief standaardwaarden en veldvalidatie.

* **Logging:**

  * Integreert met een logging utility (`logtools.get_logger`) voor statusrapportage en foutafhandeling.
  * Zorgt voor consistente logging door de hele configuratieverwerkingscyclus.

---

### Patronen en Bibliotheken

* **YAML en JSON:**

  * YAML wordt gebruikt voor configuratie-invoer, terwijl JSON optioneel kan worden gebruikt voor het opslaan van configuratiegegevens.

* **Dataclasses:**

  * Maakt gebruik van `dataclasses` voor typecontrole, standaardwaarden en eenvoudige conversie naar dicts.

* **Pathlib:**

  * Platformonafhankelijke padconstructie en bestandscontrole.

---

## Opmerkingen en TODO's

* **Versiebeheer:**

  * Het huidige versiebeheer incrementeert alleen de patch-versie (`v1.0.0`, `v1.0.1`).
  * TODO: Onderzoek of major/minor-versieverhogingen nodig zijn voor bepaalde configuratiewijzigingen.

* **Configuratievalidatie:**

  * Momenteel wordt de validatie uitgevoerd bij het laden van de configuratie.
  * TODO: Overweeg een afzonderlijke validatiemethode om de configuratie onafhankelijk van het laden te kunnen controleren.

---

## Rol in het Grotere Systeem

De `ConfigFile` klasse fungeert als een cruciale component voor het configuratiebeheer van de applicatie. Het zorgt voor:

* **Consistentie:** Alle configuratie-instellingen zijn toegankelijk via één enkele klasse.
* **Robuustheid:** Verplichte velden worden gecontroleerd en ontbrekende waarden worden aangevuld met standaardwaarden.
* **Flexibiliteit:** Door gebruik te maken van `dataclasses` kunnen nieuwe configuratievelden eenvoudig worden toegevoegd.
* **Traceerbaarheid:** Logging van configuratieproblemen, inclusief ontbrekende velden en foutieve paden.
* **Gebruiksvriendelijkheid:** Mogelijkheid om een voorbeeldconfiguratiebestand te genereren met gedetailleerde toelichting.

---

## Conclusie

De `ConfigFile` klasse is ontworpen om de configuratieverwerking in een complexe applicatie te centraliseren en te stroomlijnen. Het biedt robuuste foutafhandeling, versiebeheer voor uitvoermappen, en een eenvoudige interface voor toegang tot configuratie-gedreven paden en instellingen. Dit zorgt ervoor dat andere modules in de applicatie zich kunnen richten op hun kernfunctionaliteit, zonder zich zorgen te hoeven maken over de details van configuratiebeheer.
