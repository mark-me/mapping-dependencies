# Logtools

**Gecentraliseerde logging en foutregistratie voor Python-applicaties**

Dit pakket biedt een herbruikbare en uitbreidbare loggingconfiguratie, inclusief:

- Gecentraliseerde loggingconfiguratie (JSON-formaat)
- Logging naar stdout én naar een roterend logbestand
- Een aangepaste logging handler die waarschuwingen en fouten bijhoudt
- Een eenvoudige interface om een logger te verkrijgen en parsingproblemen te controleren

## 🚀 Snelstart

### 1. Importeer de logger en issue tracker

In elk module waar je wilt loggen:

```python
from logtools import get_logger, issue_tracker

logger = get_logger(__name__)
logger.info("Dit is een logbericht.")
logger.warning("Deze waarschuwing wordt bijgehouden.")

if issue_tracker.has_issues():
    print("Problemen gevonden:", issue_tracker.get_issues())
else:
    print("Geen problemen.")
```

### 2. Wat wordt er gelogd?

De logoutput is geformatteerd als JSON en bevat tijdstempels, niveau, bericht, module, functienaam en proces-ID. Standaard wordt er:

- Gelogd naar **stdout**
- Geschreven naar een roterend bestand genaamd `log.json`

### 3. Wat wordt er bijgehouden?

Alleen logberichten op niveau `WARNING` of hoger worden bijgehouden in het geheugen door de aangepaste `IssueTrackingHandler`. Hiermee kun je:

- Problemen loggen tijdens verwerking
- Aan het einde controleren of er fouten zijn opgetreden

## Pakketstructuur

```md
logtools/
├── __init__.py            # Publieke API: get_logger, issue_tracker
├── logging_config.py      # Loggingconfiguratie als dict
├── log_manager.py         # Past configuratie toe en stelt logger + tracker beschikbaar
└── issue_tracking.py      # Aangepaste handler die problemen bijhoudt
```

## Aanpassen

- Je kunt `logging_config.py` aanpassen om andere formatters te gebruiken of te loggen naar extra bestemmingen (zoals syslog of externe diensten).
- De `IssueTrackingHandler` kan worden uitgebreid om extra context zoals tijdstempels of thread-informatie vast te leggen.
