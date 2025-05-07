### Overzicht

Dit bestand definieert de klasse `ObjectTransformer`, die hulpmethoden biedt voor het transformeren en opschonen van datastructuren die afkomstig zijn uit Power Designer-objecten. Het hoofddoel is om het opvragen en verwerken van deze objecten te vereenvoudigen voor ETL (Extract, Transform, Load) en DDL (Data Definition Language) operaties. De klasse richt zich op het normaliseren van sleutelnamen, het converteren van tijdstempels en het extraheren van specifieke waarden uit attributenteksten, zodat de data gemakkelijker te verwerken is in downstream-processen.

---

### **Belangrijkste Componenten**

#### **ObjectTransformer (klasse)**

- De centrale klasse in het bestand, waarin alle transformatielogica voor Power Designer-objecten is ondergebracht.

---

### **Methoden:**

1. **`clean_keys(data: dict) -> dict`**
   - Verwijdert Power Designer-specifieke voorvoegsels zoals `@` en `a:` uit sleutelnamen.
   - Normaliseert sleutelnamen om de consistentie en toegankelijkheid te verbeteren voor verdere verwerking.

2. **`convert_timestamps(data: dict) -> dict`**
   - Converteert Unix-timestampvelden (bijv. `"a:CreationDate"`, `"a:ModificationDate"`) naar Python `datetime` objecten.
   - Verwerkt recursief geneste woordenboeken en lijsten.
   - Verbetert de robuustheid bij het omgaan met datums in ETL-processen.

3. **`extract_value_from_attribute_text(text: str, marker: str) -> str`**
   - Extraheert een waarde uit een string op basis van een voorafgaand kenmerk of marker.
   - Nuttig voor het parsen van uitgebreide attributenteksten waarin waarden in een specifiek formaat zijn opgenomen.

---

### **Logging:**

- Gebruikt een logger (geïmporteerd uit `log_config`) om informatieve en debug-niveau berichten te genereren tijdens het transformatieproces.
- Ondersteunt traceerbaarheid en foutopsporing.

---

### **Privé Helper Methode:**

- **`__convert_values_datetime(value)`**
  - Recursieve hulpfunctie die intern wordt gebruikt om tijdstempels om te zetten in `datetime` objecten.
  - Ondersteunt geneste structuren zoals lijsten en woordenboeken.

---

### **Rol in het Grotere Systeem:**

Dit bestand speelt een ondersteunende rol in een groter ETL- of dataverwerkingsysteem door ervoor te zorgen dat Power Designer-objectdata genormaliseerd is, tijdstempels correct getypeerd zijn en specifieke attributen betrouwbaar kunnen worden geëxtraheerd. Hierdoor wordt de complexiteit van downstream-processen verminderd en de data-integriteit gewaarborgd.
