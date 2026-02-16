import pandas as pd
from master_data import Customer
from events import publish_order

def build_master():
    crm = pd.read_csv('crm_customers.csv')
    ecommerce = pd.read_csv('ecommerce_users.csv')

    master_records = []

    for _, row in crm.iterrows():
        customer = Customer.create(
            name=row['name'],
            email=row['email'],
            phone=row.get('phone')
        )
        master_records.append(customer)

    df_master = pd.DataFrame([c.__dict__ for c in master_records])
    df_master.to_csv("customers_master.csv", index=False)

    return df_master

if __name__ == "__main__":
    master_df = build_master()
    print(master_df)
    publish_order(customer_id="abc", total=-10)
