import pandas as pd

master = pd.read_csv("customers_master.csv")
orders = pd.read_csv("erp_orders.csv")

# Converti colonne di ID a string per evitare type mismatch
master['crm_id'] = master['crm_id'].astype(str)
master['ecommerce_id'] = master['ecommerce_id'].astype(str)
orders['customer_ref'] = orders['customer_ref'].astype(str)

# Primo tentativo: match su crm_id
orders_enriched = orders.merge(
    master[['global_id', 'crm_id']],
    left_on='customer_ref',
    right_on='crm_id',
    how='left'
)

# Secondo tentativo: match su ecommerce_id
orders_enriched = orders_enriched.merge(
    master[['global_id', 'ecommerce_id']],
    left_on='customer_ref',
    right_on='ecommerce_id',
    how='left',
    suffixes=('_crm', '_ecom')
)

# Consolidamento global_id
orders_enriched['final_global_id'] = (
    orders_enriched['global_id_crm']
    .combine_first(orders_enriched['global_id_ecom'])
)

print(orders_enriched[['order_id', 'final_global_id', 'total_amount']])
