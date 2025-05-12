### Overzicht

Dit bestand definieert de klasse `ModelExtractor`, die verantwoordelijk is voor het extraheren en transformeren van relevante objecten uit een Power Designer Logical Data Model (LDM)-document. Het hoofddoel is om de inhoud van het LDM te parsen, interne en externe modellen, entiteiten, relaties, domeinen en datasources te identificeren en deze informatie voor te bereiden voor verdere verwerking, zoals ETL of lineage-analyse. De klasse maakt gebruik van twee transformatie-helpers (`TransformModelInternal` en `TransformModelsExternal`) om de specifieke structuren van interne en externe modellen te verwerken.

---

### **Belangrijkste Componenten**

#### **ModelExtractor Klasse**

De kernklasse van het bestand, waarin alle logica is ondergebracht voor het extraheren van modellen en hun componenten uit een Power Designer LDM. De klasse biedt de `models()`-methode als hoofdingang voor het ophalen van alle relevante modellen en hun bijbehorende objecten.

---

### **Initialisatie (`__init__`)**

- **Doel:** Initialiseert de extractor met de LDM-inhoud en stelt de transformatie-helpers in.
- **Voorbewerking:** Extraheert domeininformatie voor gebruik bij de verwerking van entiteiten.

---

### **models() Methode**

- Het hoofdentrypoint voor gebruikers van deze klasse.
- Orkestreert de extractie van interne en externe modellen.
- Verwerkt speciale gevallen (zoals ontbrekende shortcuts).
- Combineert resultaten in een uniforme lijst.

---

### **Interne Extractiemethoden**

- `__model_internal()`: Extraheert het hoofdmodel (intern), inclusief entiteiten, relaties en datasources.
- `__entities_internal()`: Verzamelt alle entiteiten uit het interne model, waarbij bepaalde stereotypes worden gefilterd.
- `__relationships()`: Extraheert relaties tussen entiteiten en houdt rekening met aggregaten voor referentieresolutie.
- `__datasources()`: Extraheert gegevensbroninformatie die in het model wordt gebruikt.
- `__domains()`: Extraheert domein/type-informatie voor attributen.

---

### **Externe Extractiemethoden**

- `__models_external()`: Extraheert modellen die buiten het huidige LDM worden beheerd, gebruikt voor horizontale lineage.
- `__entities_external()`: Verzamelt entiteiten uit externe modellen en ondersteunt zowel pakketgebaseerde als directe entiteit-referenties.

---

### **Gebruik van Transformatie-Helpers**

- De klasse delegeert gedetailleerde transformatielogica naar `TransformModelInternal` en `TransformModelsExternal`.
- Dit bevordert scheiding van verantwoordelijkheden en hergebruik van code.

---

### **Logging en Foutafhandeling**

- Maakt gebruik van gestructureerde logging om te waarschuwen of fouten te melden wanneer verwachte gegevens ontbreken.
- Dit vergroot de robuustheid en vergemakkelijkt debugging.

---

### **Rol in het Grotere Systeem:**

Dit bestand fungeert als een brug tussen de ruwe Power Designer LDM-inhoud en hogere dataverwerkings- of ETL-workflows. Het abstraheert de complexiteit van de LDM-structuur en biedt een overzichtelijke interface voor downstreamcomponenten om gestructureerde modelinformatie te benaderen.
