# Overzicht

Dit bestand definieert de klasse `StereotypeExtractor`, die verantwoordelijk is voor het extraheren en verwerken van specifieke typen objecten (filters, aggregaten en scalars) uit een Power Designer-document dat als een dictionary is gerepresenteerd. De extractie is gebaseerd op een opgegeven stereotype. De klasse verzorgt tevens het opschonen en transformeren van deze objecten en verzamelt gerelateerde domeingegevens. Gedurende het proces wordt logging gebruikt om debugging en traceerbaarheid te ondersteunen.

---

## **Belangrijkste Componenten**

### **StereotypeExtractor Klasse**

- **Doel:**
  - Initialiseren met Power Designer-inhoud en een target-stereotype.
  - Objecten van het opgegeven stereotype extraheren uit het model.
  - Onnodige of irrelevante velden uit deze objecten verwijderen.
  - Gerelateerde domeingegevens verzamelen en verwerken.
  - Transformatielogica delegeren naar de `TransformStereotype` klasse.

---

## **objects() Methode**

- Publieke methode die een lijst retourneert van opgeschoonde en verwerkte objecten die overeenkomen met het opgegeven stereotype.

---

### **__objects() Methode** (Privé)

- Voert de eigenlijke extractie, filtering en opschoning van objecten uit de Power Designer-inhoud uit.
- Roept transformatielogica aan via de `TransformStereotype` klasse.
- Logt essentiële stappen tijdens het extractieproces.

---

### **__domains() Methode** (Privé)

- Verzamelt en verwerkt domeingegevens die gekoppeld zijn aan de objecten.
- Zorgt ervoor dat elk object kan worden gelinkt aan zijn domein via een ID.

---

### **TransformStereotype Afhankelijkheid**

- De klasse vertrouwt op de externe `TransformStereotype` klasse (geïmporteerd uit `.pd_transform_stereotype`).
- Deze klasse verzorgt de transformatie van zowel objecten als domeinen, waardoor transformatielogica buiten de extractor wordt gehouden.

---

### **Logging**

- Maakt gebruik van een logger (uit een `log_config` module) om debug- en foutmeldingen te genereren.
- Dit helpt bij het monitoren en oplossen van problemen tijdens het extractieproces.

---

### **Samenvatting:**

Dit bestand speelt een essentiële rol in het systeem door de logica te isoleren voor het extraheren, opschonen en voorbereiden van Power Designer-modelobjecten op basis van hun stereotype. Het zorgt voor een gestructureerde aanpak door transformaties uit te besteden aan een aparte helperklasse, wat de onderhoudbaarheid en leesbaarheid van de code ten goede komt.
