# Overzicht

Dit bestand definieert de klasse `TransformSourceComposition`, die verantwoordelijk is voor het transformeren, opschonen en verrijken van "source composition"-datastructuren die zijn geëxtraheerd uit Power Designer Logical Data Model (LDM)-documenten. Het hoofddoel is om complexe mapping- en compositiedata te verwerken en te normaliseren. Hierbij worden voorbeelddata verwijderd, relevante entiteiten, join-condities en scalar-condities geëxtraheerd en klaargemaakt voor verdere verwerking in ETL- of DDL-generatie.

De klasse breidt `ObjectTransformer` uit en bevat een reeks methoden voor het afhandelen van de hiërarchische en soms inconsistente structuur van de door Power Designer geëxporteerde data, met een focus op mappingcomposities, join-condities, broncondities en scalair-expressies.

---

## Belangrijkste Componenten

### TransformSourceComposition (klasse)

* **Doel:** Centraliseert de logica voor het transformeren van source composition-data uit Power Designer-mappings, zodat deze geschikt worden voor downstream-verwerking.
* **Erft van:** `ObjectTransformer`, vermoedelijk om generieke transformatiehulpmethoden te hergebruiken.

---

### Belangrijkste Methode: `source_composition`

* **Rol:** Entreepunt voor het transformeren van de compositiedata van een enkele mapping.
* **Verantwoordelijkheden:**

  * Reinigt en normaliseert de compositiestructuur.
  * Verwijdert voorbeeldcomposities (MDDE).
  * Verwerkt compositie-items (`FROM`, `JOIN`, etc.).
  * Verrijkt mappings met datasource-informatie.
  * Filtert ongewenste scalar business rule items uit.

---

### Compositie Verwerkingsmethoden

* **`compositions_remove_mdde_examples`**

  * Verwijdert voorbeeldcomposities, met de aanname dat er slechts één echte compositie per mapping aanwezig is.

* **`__composition`**

  * Reinigt en verrijkt een enkele compositie.
  * Extraheert join-typen, aliassen en betrokken entiteiten.

* **`__composition_entity`**

  * Resolveert en verrijkt de entiteit die betrokken is bij een compositie.

* **`__composition_join_conditions`**

  * Verwerkt join-condities door operators te extraheren en parent/child-attributen te koppelen.

* **`__join_condition_components`**

  * Normaliseert de componenten (attributen/entiteiten) die betrokken zijn bij een join-conditie.

---

### Bron- en Scalar-conditiemethoden

* **`__composition_source_conditions`**

  * Verwerkt broncondities (`filter`) voor een compositie, waarbij variabelen en literals worden geëxtraheerd.

* **`__source_condition_components`**

  * Verwerkt de componenten van een bronconditie en koppelt ze aan attributen en aliassen.

* **`__composition_scalar_conditions`**

  * Verwerkt scalar-condities door SQL-expressies bij te werken en variabelen te vervangen.

* **`__scalar_condition_components`**

  * Extraheert en normaliseert de componenten van een scalar-conditie.

---

### Mapping en Hulpmethoden

* **`__mapping_datasource`**

  * Verrijkt de mapping met de correcte datasource-code.

* **`__mapping_update`**

  * Actualiseert attributenmappings om gegenereerde expressies te gebruiken in plaats van entiteit-aliassen.

* **`__extract_value_from_attribute_text`**

  * Hulpmethode om specifieke waarden uit attributentekstblokken te extraheren op basis van een vooraf bepaald prefix.

---

### Logging en Foutafhandeling

* Uitgebreid gebruik van logging voor debugging, waarschuwingen en informatieve meldingen.
* Vooral gericht op het detecteren van onverwachte datastructuren of ontbrekende velden.

---

### Patronen en Opvallende Praktijken

* **Data Opschoning en Normalisatie:** Veel methoden controleren en converteren tussen dicts en lijsten om de inconsistente datastructuur van de inputdata af te handelen.
* **Hiërarchische Verwerking:** De klasse verwerkt geneste structuren, waarbij entiteiten, attributen en condities op meerdere niveaus worden afgehandeld.
* **Aannames:**

  * Er wordt uitgegaan van slechts één echte compositie per mapping.
  * Bepaalde stereotypes (bijvoorbeeld `mdde_ScalarBusinessRule`) worden gefilterd.

---

### Rol in het Grotere Systeem

Deze klasse is een kerncomponent binnen een data lineage- of ETL-codebase. Ze transformeert complexe, geneste compositiedata uit Power Designer naar een genormaliseerde en verrijkte structuur, klaar voor verdere verwerking in ETL- of DDL-workflows. De nadruk ligt op data-integratie, referentiekoppelingen en dataopschoning.
