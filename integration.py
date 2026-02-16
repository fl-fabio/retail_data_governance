import pandas as pd

master = pd.read_csv("customers_master.csv")
orders = pd.read_csv("erp_orders.csv")
crm = pd.read_csv("crm_customers.csv")

orders['customer_ref'] = orders['customer_ref'].astype(str)
crm['id'] = crm['id'].astype(str)

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