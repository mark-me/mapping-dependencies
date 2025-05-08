### Overzicht

Dit bestand definieert de klasse `CodeList`, die verantwoordelijk is voor het lezen, transformeren en exporteren van codelijstdata. De focus ligt op het standaardiseren van data uit verschillende bronsystemen ("DMS" en "AGS") en het opslaan van de verzamelde data in een JSON-formaat voor verdere verwerking door andere componenten in het systeem.

De klasse maakt gebruik van efficiënte dataframes (`Polars`), YAML voor configuratie, JSON voor output en logging voor procesbewaking.

---

### Belangrijkste Componenten

#### CodeList (klasse)

* **Doel:** Centraliseert de logica voor het lezen, transformeren en exporteren van codelijsten.
* **Initialisatie:**

  * Accepteert paden voor input- en outputmappen.
  * Initialiseert een lijst (`self.lst_codeList`) om de verzamelde codelijsten op te slaan.

---

### Belangrijkste Methode: `read_CodeLists()`

* **Rol:** Coördineert het lezen van codelijsten uit zowel "DMS"- als "AGS"-bronsystemen.
* **Werking:**

  * Roept de privé-methoden `__read_DMS_CodeList()` en `__read_AGS_CodeList()` aan voor het lezen van Excel-bestanden.
  * Voeg een "SourceSystem"-kolom toe om de herkomst van de data vast te leggen.
  * Aggregreert de data in `self.lst_codeList` als een lijst van dictionaries.

---

### Privé Methodes

#### `__read_DMS_CodeList()` / `__read_AGS_CodeList()`

* **Doel:** Verwerken van codelijstbestanden per bronsysteem.
* **Werking:**

  * Bepaalt de bronmap op basis van configuratie.
  * Leest Excel-bestanden met een specifieke sheetnaam.
  * Verwijdert onnodige kolommen en hernoemt kolommen om een gestandaardiseerd formaat te creëren.
  * Vult lege waarden en converteert de data naar een lijst van dictionaries.
  * Voegt een "SourceSystem"-kolom toe met de waarde "DMS" of "AGS".

---

### Exportmethode: `write_CodeLists

* **Doel:** Serialiseert de verzamelde codelijstdata naar een JSON-bestand.
* **Output:** De JSON-structuur wordt weggeschreven naar het opgegeven pad, zodat andere componenten (bijv. een publisherklasse) de data kunnen gebruiken.

---

### Script Entry

* **Configuratielading:**

  * Leest een YAML-configuratiebestand om input- en outputpaden op te halen.

* **Uitvoeringsstroom:**

  * Instantieert de `CodeList`-klasse.
  * Start het leesproces (`read_CodeLists()`).
  * Schrijft de verzamelde data weg (`write_CodeLists()`).
  * Drukt een voltooiingsbericht af.

---

### Opvallende Patronen en Gebruikte Libraries

* **Polars:** Voor snelle DataFrame-operaties en Excel-bestandsverwerking.
* **YAML en JSON:** Voor configuratie-instellingen en outputserialisatie.
* **Logging:** Voor zichtbaarheid tijdens het proces en voor het melden van mogelijke dataproblemen, zoals meerdere bestanden in een bronmap.
* **Pathlib:** Voor consistente padmanipulatie en -controle.

---

### Rol in het Grotere Systeem

Dit bestand fungeert als een data-voorbereidingsmodule die codelijstgegevens uit meerdere bronnen samenvoegt en standaardiseert. De gestandaardiseerde data wordt weggeschreven in JSON-formaat voor verdere verwerking door andere componenten, zoals een publicatie- of rapportagecomponent. Het vormt daarmee een essentiële stap in een bredere ETL- of data-integratiepijplijn.
