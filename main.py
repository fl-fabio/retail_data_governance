import pandas as pd
import uuid

crm = pd.read_csv("crm_customers.csv")
ecommerce = pd.read_csv("ecommerce_users.csv")

# Join su email come chiave di riconciliazione
reconciled = pd.merge(
    crm,
    ecommerce,
    left_on="email",
    right_on="email_address",
    how="outer"
)

master_records = []

for _, row in reconciled.iterrows():
    master_records.append({
        "global_id": str(uuid.uuid4()),
        "crm_id": row.get("id"),
        "ecommerce_id": row.get("user_id"),
        "email": row.get("email") or row.get("email_address")
    })

master_df = pd.DataFrame(master_records)
master_df.to_csv("customers_master.csv", index=False)
print(master_df)
