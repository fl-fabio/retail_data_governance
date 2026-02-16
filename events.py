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


"""
Part 2
"""
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