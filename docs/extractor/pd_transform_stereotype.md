### Overzicht

Dit bestand definieert de klasse `TransformSourceComposition`, die verantwoordelijk is voor het transformeren, opschonen en verrijken van "source composition"-datastructuren die zijn geëxtraheerd uit Power Designer Logical Data Model (LDM)-documenten. Het hoofddoel is om complexe, geneste mappingdata te verwerken en te normaliseren, met een focus op de samenstelling van bronentiteiten, join-condities en scalar/filter business rules, zodat deze geschikt zijn voor verdere verwerking in data lineage, DDL of ETL-generatie.

De klasse breidt `ObjectTransformer` uit en biedt methoden om:

- Voorbeeldcomposities te verwijderen,
- Compositie-items (zoals FROM, JOIN, APPLY clausules) te parseren en verrijken,
- Join- en broncondities te extraheren en te verwerken,
- Scalar business rules en hun SQL-expressies te verwerken,
- Attribuutmappings bij te werken met gegenereerde expressies,
- Datasource-informatie te integreren.

Logging wordt uitgebreid gebruikt voor debugging en waarschuwingen over onverwachte datastructuren.

---

### **Belangrijkste Componenten**

#### **TransformSourceComposition (klasse)**

- **Doel:** Centrale klasse voor het transformeren en verrijken van source composition-data uit Power Designer mappings.
- **Erft van:** `ObjectTransformer` (vermoedelijk voor gedeelde transformatiehulpmethoden).

---

### **Methoden:**

1. **`source_composition(mapping: dict) -> dict`**
   - **Functie:** Entreepunt voor het transformeren van de source composition van een mapping.
   - **Proces:**
     - Verwijdert voorbeeldcomposities,
     - Verwerkt compositie-items (FROM, JOIN, APPLY),
     - Verrijkt de mapping met opgewerkte data.

2. **Samenstelling Verwerkingsmethoden:**
   - **`compositions_remove_mdde_examples(compositions: list) -> list`**
     - Verwijdert voorbeeldcomposities, waarbij wordt aangenomen dat er slechts één echte compositie per mapping is.

   - **`__composition(composition: dict) -> dict`**
     - Reinigt en verrijkt een enkele compositie.
     - Bepaalt join-typen en verwerkt specifieke clausules.

   - **`__composition_entity(entity: dict) -> dict`**
     - Resolving en verrijken van een entiteit in een compositie.

   - **`__composition_join_conditions(join: dict) -> dict`**
     - Verwerkt join-condities, waarbij operators en attributen worden geëxtraheerd.

   - **`__join_condition_components(condition: dict) -> dict`**
     - Verrijkt de linker- en rechterzijde van een join-conditie.

---

### **Bron- en Scalar-conditiemethoden:**

- **`__composition_source_conditions(source_conditions: list) -> list`**
  - Verwerkt broncondities voor filter business rules.

- **`__source_condition_components(condition: dict) -> dict`**
  - Verrijkt componenten van een bronconditie.

- **`__composition_scalar_conditions(scalar_conditions: list) -> list`**
  - Verwerkt scalar business rules en voegt gegenereerde SQL-expressies toe.

- **`__scalar_condition_components(condition: dict) -> dict`**
  - Verrijkt componenten van een scalar-conditie.

---

### **Mapping Update Methodes:**

- **`__mapping_datasource(mapping: dict, datasource: str) -> dict`**
  - Verrijkt de mapping met de bijbehorende datasource-code.

- **`__mapping_update(mapping: dict, generated_expressions: dict) -> dict`**
  - Actualiseert attributenmapping met gegenereerde expressies, vooral wanneer een bronattribuut verwijst naar een scalar.

---

### **Hulpmethode:**

- **`__extract_value_from_attribute_text(text: str, marker: str) -> str`**
  - Extraheert specifieke waarden uit attributentekstblokken voor het parsen van join-typen, aliassen en operators.

---

### **Patronen en Praktijken:**

- **Data Opschoning:** Veel methoden beginnen met het normaliseren van sleutels en het afhandelen van gevallen waarin lijsten onverwacht woordenboeken zijn.
- **Logging:** Uitgebreid gebruik van logging voor traceerbaarheid en foutopsporing.
- **Aannames:** Er wordt vanuit gegaan dat er slechts één echte compositie per mapping overblijft na het verwijderen van voorbeelden.
- **Domeinspecifieke Logica:** Gericht op de XML-structuur van Power Designer en de MDDE-conventies (Model-Driven Data Engineering).

---

### **Rol in het Grotere Systeem:**

Dit bestand vormt een kernonderdeel van een data lineage- of ETL-codebase, waarbij complexe, geneste mappingdata uit Power Designer op een bruikbare manier worden getransformeerd voor verdere verwerking. Het zorgt voor een consistente structuur, verwijdert ruis en verrijkt de data met extra context, waardoor de kwaliteit en bruikbaarheid van downstream-processen wordt verbeterd.
