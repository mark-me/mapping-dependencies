# Overzicht

Dit bestand definieert de klasse `MappingExtractor`, die verantwoordelijk is voor het extraheren van ETL (Extract, Transform, Load) mappingspecificaties uit een Power Designer Logical Data Model (LDM) dat gebruikmaakt van de CrossBreeze MDDE-extensie. De klasse verwerkt de ruwe modelgegevens, filtert irrelevante mappings eruit en transformeert de geëxtraheerde informatie naar een leesbaarder en gestructureerd formaat met behulp van meerdere transformatie-helpers.

---

## **Belangrijkste Componenten**

### **Imports en Logging**

- Importeert drie transformatieklassen:
  - `TransformAttributeMapping`
  - `TransformSourceComposition`
  - `TransformTargetEntity`
  Deze klassen encapsuleren specifieke transformatielogica voor verschillende aspecten van het mapping-extractieproces.
- Configureert een logger voor debugging en traceerbaarheid.

---

### **MappingExtractor Klasse**

- **Doel:** Centrale klasse voor het orkestreren van de extractie en transformatie van mappinggegevens uit de Power Designer LDM-inhoud.
- **Initialisatie (`__init__`):**
  - Accepteert de LDM-inhoud als een dictionary.
  - Initialiseert de transformatie-helpers.

**mappings Methode:**

- **Input:** Lijsten van objecten, attributen, variabelen en datasources uit de LDM.
- **Proces:**
  - Lokaliseert de relevante mappingdefinities binnen de LDM-inhoud.
  - Filtert mappings die moeten worden genegeerd (bijv. voorbeeld- of testmappings).
  - Voor elke mapping:
    - Identificeert target-entiteiten.
    - Mergeert attributen en variabelen voor verdere verwerking.
    - Extraheert attributenmappings en broncomposities met behulp van de helperklassen.
    - Aggregateert de getransformeerde mappingdefinities in een eindlijst.
- **Output:** Retourneert een lijst van verwerkte mapping-objecten, klaar voor verdere verwerking of export.

---

### **Transformatie-Helperklassen**

Hoewel niet geïmplementeerd in dit bestand, duidt het gebruik van `TransformAttributeMapping`, `TransformSourceComposition` en `TransformTargetEntity` op een modulaire opzet.

- Elke klasse is verantwoordelijk voor een specifiek aspect van het mapping-transformatieproces.
- Dit bevordert herbruikbaarheid en overzichtelijkheid van de code.

---

## **Samenvatting:**

Dit bestand dient als het belangrijkste entrypoint voor het extraheren en transformeren van ETL-mappingspecificaties uit Power Designer LDM-bestanden. Het biedt een gestructureerde en uitbreidbare aanpak door specifieke transformatietaken te delegeren aan afzonderlijke helperklassen, wat zorgt voor onderhoudbaarheid en duidelijkheid in de mapping-extractieworkflow.
