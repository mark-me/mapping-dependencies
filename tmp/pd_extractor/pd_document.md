Dit bestand definieert de klasse `PDDocument`, die verantwoordelijk is voor het extraheren, transformeren en serialiseren van gegevens uit een Power Designer Logical Data Model (LDM)-bestand. De klasse biedt methoden om de LDM XML te parsen, verschillende modelcomponenten te extraheren (zoals entiteiten, filters, scalars, aggregaten en mappings) en de verwerkte gegevens in een gestructureerd JSON-formaat uit te voeren. Deze output dient als input voor downstreamprocessen zoals de generatie van DDL en ETL.

Het bestand bevat ook een command-line entry point dat configuratie leest uit een YAML-bestand, het opgegeven LDM-bestand verwerkt en het resulterende JSON-bestand naar schijf schrijft.

### Belangrijkste Componenten

#### **PDDocument Klasse**

- **Doel:** Centrale klasse voor het verwerken van Power Designer LDM-bestanden.
- **Initialisatie:** Laadt en parseert de LDM XML in een dictionary-structuur voor verdere verwerking.

**Extractiemethoden:**

- `get_filters()`, `get_scalars()`, `get_aggregates()`: Extraheert bedrijfsregels (filters, scalars, aggregaten) met behulp van de `StereotypeExtractor`.
- `get_models()`: Extraheert modelgegevens (entiteiten, attributen, etc.) met behulp van de `ModelExtractor`.
- `get_mappings()`: Extraheert ETL-mappings met behulp van de `MappingExtractor`, waarbij informatie uit entiteiten, filters, scalars, aggregaten, variabelen, attributen en datasources wordt gecombineerd.

**Hulpmethoden:**

- Private methoden (voorafgegaan door `__all_`) aggregeren en organiseren geëxtraheerde gegevens over modellen, zoals entiteiten, filters, scalars, aggregaten, attributen, variabelen en datasources.

**Serialisatie:**

- `write_result()` compileert alle geëxtraheerde gegevens in een dictionary en schrijft deze weg als een JSON-bestand, waarbij datetime-serialisatie en directorycreatie worden afgehandeld.

---

### **Ondersteunende Extractors en Transformers**

- `ModelExtractor`, `StereotypeExtractor`, `MappingExtractor`, `ObjectTransformer`: Dit zijn geïmporteerde helperklassen (vermoedelijk elders in het project gedefinieerd) die de logica encapsuleren voor het extraheren van specifieke soorten informatie uit de geparste LDM-inhoud.

---

### **Logging**

- Maakt gebruik van een geconfigureerde logger voor informatieve, debug- en waarschuwingsberichten gedurende het extractie- en serialisatieproces.

---

### **Command-Line Entry Point**

- Leest configuratie uit een YAML-bestand.
- Instantieert `PDDocument` met het opgegeven LDM-bestand.
- Roept `write_result()` aan om het geëxtraheerde model- en mapping-gegevens naar een JSON-bestand te schrijven.
- Logt de voltooiingsstatus.

---

### **Rol in het Grotere Systeem:**

Dit bestand fungeert als de hoofdinterface voor het omzetten van Power Designer LDM-bestanden in een gestructureerd, machineleesbaar formaat dat geschikt is voor verdere verwerking in datamodellering, DDL- en ETL-generatie workflows. Het abstraheert de complexiteit van het parsen en interpreteren van de LDM XML en biedt een overzichtelijke API voor downstream-tools en -processen.
