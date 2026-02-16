## Dalla frammentazione informativa all’architettura target: progettare e ridurre il Data Debt

### Introduzione al problema

L’azienda oggetto del laboratorio è una media impresa retail che opera sia online sia tramite punti vendita fisici. Nel tempo ha adottato soluzioni software diverse, ciascuna introdotta per rispondere a esigenze specifiche: un CRM per la gestione dei clienti, una piattaforma e-commerce separata, un ERP per gli ordini e la fatturazione, fogli Excel utilizzati dal marketing e reportistica costruita tramite esportazioni manuali.

L’organizzazione non ha mai definito un dominio dati formalizzato, né un’architettura target dell’ecosistema informativo. Ogni sistema è cresciuto in modo autonomo. L’assenza di una visione unitaria ha generato duplicazioni, incoerenze e dipendenze operative difficili da gestire.

Questo laboratorio simula una situazione reale in cui il Data Manager deve:

– analizzare lo stato attuale
 – identificare il debito informativo
 – progettare un’architettura target coerente
 – definire una roadmap evolutiva
 – implementare una prima riduzione concreta del data debt

L’obiettivo non è solo produrre codice funzionante, ma dimostrare come le scelte architetturali riducano la complessità nel lungo periodo.

### Fase 1 – Analisi dello stato attuale

L’azienda dispone di tre sorgenti principali:

CRM:

```
id,name,email,phone
1,Mario Rossi,mario@email.it,333123
2,Luisa Bianchi,luisa@email.it,334555
```

E-commerce:

```
user_id,full_name,email_address
A01,M. Rossi,mario@email.it
A02,Luisa B.,luisa@email.it
```

ERP:

```
order_id,customer_ref,total_amount
1001,1,250
1002,A02,180
```

È evidente che non esiste un identificatore globale del cliente. Il CRM utilizza un id numerico, l’e-commerce utilizza un codice alfanumerico, l’ERP referenzia entrambi. L’unico elemento potenzialmente stabile è l’email.

Questa frammentazione rappresenta un caso tipico di debito informativo: l’integrazione è fragile, il matching è implicito, l’analisi cross-canale richiede lavoro manuale.

Per iniziare, si costruisce uno script di analisi che evidenzi le incongruenze.

### Creazione del file `analysis.py`

```python
import pandas as pd

crm = pd.read_csv("crm_customers.csv")
ecommerce = pd.read_csv("ecommerce_users.csv")
orders = pd.read_csv("erp_orders.csv")

print("CRM")
print(crm)

print("\nE-commerce")
print(ecommerce)

print("\nERP Orders")
print(orders)
```

Questo primo passo non risolve nulla, ma rende esplicito il problema. La governance inizia sempre dalla visibilità.

### Fase 2 – Evidenziare il debito informativo

Ora si tenta di capire quanti clienti coincidono tra CRM ed e-commerce utilizzando l’email come chiave logica.

Aggiorniamo `analysis.py`:

```python
crm_emails = crm[['id', 'email']]
ecommerce_emails = ecommerce[['user_id', 'email_address']]

merged = pd.merge(
    crm_emails,
    ecommerce_emails,
    left_on='email',
    right_on='email_address',
    how='outer',
    indicator=True
)

print("\nConfronto CRM vs E-commerce")
print(merged)
```

L’output mostrerà che i clienti sono duplicati semanticamente ma identificati in modo diverso. L’ERP poi utilizza riferimenti misti, rendendo complessa la riconciliazione.

Il debito informativo emerge chiaramente: ogni nuovo caso d’uso analytics richiederebbe logiche ad hoc.

### Fase 3 – Definizione dell’architettura target

A questo punto si introduce il concetto di architettura target. L’obiettivo è centralizzare il dominio Cliente attraverso un Golden Record e introdurre un identificatore globale unico.

Si crea una nuova struttura di progetto:

```
retail_data_governance/
│
├── analysis.py
├── master_data.py
├── events.py
├── crm_customers.csv
├── ecommerce_users.csv
├── erp_orders.csv
└── customers_master.csv
```

### Fase 4 – Modellazione del Golden Record

Nel file `master_data.py` si definisce il modello unificato.

```python
from dataclasses import dataclass
import uuid

@dataclass
class Customer:
    global_id: str
    name: str
    email: str
    phone: str | None = None

    @staticmethod
    def create(name, email, phone=None):
        return Customer(
            global_id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=phone
        )
```

Qui avviene il primo passo di riduzione del debito: si introduce una sorgente autorevole.

### Fase 5 – Costruzione del Master Data

Nel file main.py` si aggiunge la logica di unificazione.

```python
import pandas as pd
from master_data import Customer

def build_master():
    crm = pd.read_csv("crm_customers.csv")
    ecommerce = pd.read_csv("ecommerce_users.csv")

    master_records = []

    for _, row in crm.iterrows():
        customer = Customer.create(
            name=row["name"],
            email=row["email"],
            phone=row["phone"]
        )
        master_records.append(customer)

    df_master = pd.DataFrame([c.__dict__ for c in master_records])
    df_master.to_csv("customers_master.csv", index=False)

    return df_master

if __name__ == "__main__":
    df = build_master()
    print(df)
```

Ora esiste un file `customers_master.csv` con identificatori globali coerenti.

Il debito informativo viene ridotto perché esiste una chiave universale.

### Fase 6 – Collegamento ordini al Golden Record

Si aggiorna l’ERP per collegarlo al nuovo global_id.

Creiamo `integration.py`.

```python
import pandas as pd

master = pd.read_csv("customers_master.csv")
orders = pd.read_csv("erp_orders.csv")
crm = pd.read_csv("crm_customers.csv")

orders_with_email = orders.merge(
    crm[['id', 'email']],
    left_on='customer_ref',
    right_on='id',
    how='left'
)

orders_enriched = orders_with_email.merge(
    master[['global_id', 'email']],
    on='email',
    how='left'
)

print(orders_enriched[['order_id', 'global_id', 'total_amount']])
```

Ora ogni ordine può essere associato a un identificatore globale.

Questo rappresenta un primo passo concreto verso l’architettura target.

### Fase 7 – Introduzione del modello Event-Driven

L’architettura target prevede l’introduzione di eventi strutturati.

Nel file `events.py`:

```python
from dataclasses import dataclass
from datetime import datetime
import uuid
import json

@dataclass
class OrderPlaced:
    event_id: str
    customer_id: str
    total: float
    timestamp: str

    @staticmethod
    def create(customer_id, total):
        return OrderPlaced(
            event_id=str(uuid.uuid4()),
            customer_id=customer_id,
            total=total,
            timestamp=datetime.utcnow().isoformat()
        )

def publish_order(customer_id, total):
    event = OrderPlaced.create(customer_id, total)
    print(json.dumps(event.__dict__, indent=2))
```

L’evento ora è formalizzato, indipendente dal sistema ERP originario. Questo è un passaggio fondamentale verso una riduzione strutturale del debito.

### Fase 8 – Roadmap evolutiva simulata

Nel repository deve essere presente anche un file `ROADMAP.md` in cui gli si descrive in modo discorsivo:

Fase 1: consolidamento dominio Cliente
 Fase 2: introduzione eventi
 Fase 3: abilitazione analytics

La roadmap collega scelte tecniche a obiettivi strategici, dimostrando che l’architettura target non è un diagramma ma un percorso governato.

### Risultato Finale Atteso

Alla fine del laboratorio, la repository dovrà contenere:

– codice per analisi stato attuale
 – implementazione Golden Record
 – integrazione ordini
 – modellazione evento OrderPlaced
 – documento di valutazione del debito informativo
 – roadmap evolutiva

### Fase 9 – Formalizzazione del Data Contract

Si crea una nuova cartella nel repository:

```
retail_data_governance/
│
├── contracts/
│   ├── customer_contract_v1.json
│   └── order_placed_contract_v1.json
```

### Data Contract – Customer v1

contracts/customer_contract_v1.json

```json
{
  "contract_name": "Customer",
  "version": "1.0.0",
  "owner": "Customer Domain Team",
  "description": "Golden Record for unified customer identity",
  "fields": {
    "global_id": {
      "type": "string",
      "required": true,
      "description": "Universally unique customer identifier"
    },
    "name": {
      "type": "string",
      "required": true,
      "description": "Full legal name of the customer"
    },
    "email": {
      "type": "string",
      "required": true,
      "format": "email"
    },
    "phone": {
      "type": "string",
      "required": false
    }
  }
}
```

### Data Contract – OrderPlaced v1

contracts/order_placed_contract_v1.json

```python
{
  "contract_name": "OrderPlaced",
  "version": "1.0.0",
  "owner": "Order Domain Team",
  "description": "Event emitted when an order is confirmed",
  "fields": {
    "event_id": {
      "type": "string",
      "required": true
    },
    "customer_id": {
      "type": "string",
      "required": true
    },
    "total": {
      "type": "number",
      "required": true,
      "minimum": 0
    },
    "timestamp": {
      "type": "string",
      "required": true
    }
  }
}
```

### Fase 10 – Validazione automatica del contratto

Ora si introduce un controllo automatico per prevenire violazioni.

Creiamo `contract_validator.py`.

```python
import json

def load_contract(path):
    with open(path, "r") as f:
        return json.load(f)

def validate_payload(payload, contract):
    errors = []

    fields = contract["fields"]

    for field_name, rules in fields.items():
        if rules.get("required") and field_name not in payload:
            errors.append(f"Missing required field: {field_name}")

        if field_name in payload:
            value = payload[field_name]
            expected_type = rules.get("type")

            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Field {field_name} must be string")

            if expected_type == "number" and not isinstance(value, (int, float)):
                errors.append(f"Field {field_name} must be number")

            if expected_type == "number" and "minimum" in rules:
                if value < rules["minimum"]:
                    errors.append(f"Field {field_name} must be >= {rules['minimum']}")

    return errors
```

### Fase 11 – Collegamento del contratto all’evento

Modifichiamo `events.py` per validare l’evento prima della pubblicazione.

```python
from contract_validator import load_contract, validate_payload

def publish_order(customer_id, total):
    event = OrderPlaced.create(customer_id, total)
    payload = event.__dict__

    contract = load_contract("contracts/order_placed_contract_v1.json")
    errors = validate_payload(payload, contract)

    if errors:
        raise Exception(f"Contract violation: {errors}")

    print("Event valid according to contract")
    print(payload)
```

Ora nessun evento può essere emesso se viola il contratto.

Questo riduce il debito futuro.

### Fase 12 – Simulazione di violazione

Occorre provare a :

```python
publish_order(customer_id="abc", total=-10)
```

Il sistema deve bloccare l’evento perché `total` non rispetta il minimo definito.

Qui avviene un passaggio concettuale fondamentale:
 il Data Contract non è documentazione, è enforcement.

### Fase 13 – Versionamento del Data Contract

Si introduce un principio chiave di governance: i contratti sono versionati semanticamente.

Se in futuro si aggiunge un campo obbligatorio, la versione diventa 2.0.0.

Gli studenti devono creare:

```
order_placed_contract_v2.json
```

e discutere:

- backward compatibility
- impatto sui consumer
- strategia di migrazione

Qui entra in gioco la roadmap evolutiva.

### Impatto Architetturale

Con l’introduzione dei Data Contract:

- il dominio Cliente è formalizzato
- l’evento OrderPlaced è governato
- le modifiche future sono controllate
- il debito informativo non cresce silenziosamente

L’architettura target diventa verificabile.

