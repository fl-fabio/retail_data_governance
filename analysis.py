import pandas as pd

crm = pd.read_csv('crm_customers.csv')
ecommerce = pd.read_csv('ecommerce_users.csv')
orders = pd.read_csv('erp_orders.csv')

print("CRM")
print(crm)

print("\nE-commerce")
print(ecommerce)

print("\nERP Orders")
print(orders)

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