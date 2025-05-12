# Publisher

## Overzicht

Dit bestand definieert een Python-hulpprogramma voor het programmatisch bijwerken van een Visual Studio SQL-projectbestand (`.sqlproj`) door nieuwe SQL-bestanden, mappen en post-deployment scripts toe te voegen die elders in het systeem zijn gegenereerd. De centrale klasse, `DDLPublisher`, leest een JSON-bestand dat de gegenereerde DDL-bestanden beschrijft en werkt het projectbestand bij om ervoor te zorgen dat het project synchroon blijft met de gegenereerde artefacten.

**Doelen:**

* **Consistentie:** Zorgt ervoor dat alle gegenereerde artefacten in de projectstructuur worden opgenomen.
* **Traceerbaarheid:** Logt alle wijzigingen voor later gebruik of auditing.
* **Automatisering:** Vermindert handmatig werk en voorkomt potentiële fouten door inconsistenties in de projectstructuur.

Dit zorgt voor een naadloze integratie van nieuwe SQL-scripts in de Visual Studio-omgeving en draagt bij aan een gestroomlijnde implementatiepijplijn.

### Uitvoerbeheer

* **JSON Outputbestand (`generated_ddls.json`):**

  * Dit bestand bevat een overzicht van alle gegenereerde DDL-bestanden, gestructureerd per map of type.
  * Wordt gebruikt als input voor de `publish()`-methode om nieuwe bestanden en mappen te identificeren.

* **SQL Projectbestand (`.sqlproj`):**

  * De `.sqlproj`-structuur wordt bijgewerkt met nieuwe bestanden en post-deployment scripts.
  * Problematische XML-elementen, zoals dubbele `<VisualStudioVersion>`-elementen, worden verwijderd om laadfouten in Visual Studio te voorkomen.

## Belangrijkste Componenten

### DDLPublisher (klasse)

* **Doel:**

  * Automatiseert het proces van het toevoegen van nieuwe SQL-bestanden, mappen en post-deployment scripts aan een Visual Studio SQL-projectbestand.

* **Constructor:**

  * Neemt twee paden als argumenten:

    * Het pad naar het `.sqlproj`-bestand.
    * Het pad naar het JSON-bestand dat de gegenereerde DDL-bestanden beschrijft.

* **Methoden:**

  * `publish()`

    * Leest het JSON-bestand met de gegenereerde DDL-bestanden.
    * Parseert het `.sqlproj`-bestand als XML.
    * Verwijdert problematische of dubbele `<VisualStudioVersion>`-elementen om laadfouten in Visual Studio te voorkomen.
    * Voegt nieuwe mappen, bestanden en post-deployment scripts toe aan het projectbestand indien deze nog niet aanwezig zijn.
    * Schrijft de bijgewerkte XML terug naar het projectbestand.
    * Logt alle wijzigingen voor traceerbaarheid.

---

### Uitvoeringsstroom als Script

Wanneer het script rechtstreeks wordt uitgevoerd (`__main__` sectie):

1. **Configuratie Laden:**

   * Laadt paden uit een YAML-bestand (`config.yml`).
   * Specificeert het pad naar het projectbestand (`.sqlproj`) en het JSON-bestand (`generated_ddls.json`).

2. **Initialisatie van DDLPublisher:**

   * Creëert een `DDLPublisher`-instantie met de opgegeven paden.

3. **Uitvoeren van de publicatie:**

   * Roept de `publish()`-methode aan om de nieuwe DDL-bestanden toe te voegen aan het projectbestand.

---

### Interne Methodologie

* **`publish()` Methode:**

  * Laadt het JSON-bestand (`generated_ddls.json`) en verwerkt de inhoud als een dictionary.
  * Open het `.sqlproj`-bestand als XML en converteert dit naar een bewerkbare dictionary via `xmltodict`.
  * Itereert over alle bestanden in het JSON-bestand en controleert of deze al aanwezig zijn in het projectbestand.
  * Voegt nieuwe bestanden en mappen toe aan de `<ItemGroup>`-elementen in de XML-structuur.
  * Schrijft de bijgewerkte XML-structuur terug naar het projectbestand.

---

### Belangrijke Patronen en Bibliotheken

* **XML Manipulatie:**

  * `xmltodict` wordt gebruikt voor het omzetten van XML naar een bewerkbare dictionary-structuur.
  * Dit maakt het eenvoudig om XML-elementen te bewerken en nieuwe bestanden of mappen toe te voegen.

* **Logging:**

  * Integreert met een aangepaste loggingconfiguratie om processtappen en fouten te registreren.
  * Elke wijziging in het projectbestand wordt gelogd voor auditdoeleinden.

* **Padbeheer:**

  * `pathlib.Path` wordt gebruikt voor platformonafhankelijke padconstructie en -controle.

* **Configuratiebeheer:**

  * De YAML-configuratie maakt het eenvoudig om paden en instellingen centraal te beheren.

---

### Opmerkingen en TODO's

* **XML-Element Volgorde:**

  * In de huidige implementatie kunnen nieuwe `<ItemGroup>`-elementen willekeurig worden toegevoegd.
  * TODO: Overweeg om de volgorde van XML-elementen te optimaliseren, zodat nieuwe bestanden en scripts in logische groepen worden geplaatst.

* **Alternatieve Strategieën:**

  * Een mogelijke verbetering is het bijhouden van nieuwe bestanden in een aparte `includelist.json` in plaats van in het `.sqlproj`-bestand zelf.
