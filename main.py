import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import matplotlib.pyplot as plt

# Define your database connection parameters
db_config_cilantro = {
    "host": "cliantro.cmbrsga0s9bx.me-central-1.rds.amazonaws.com",
    "port": 3306,
    "user": "cilantro",
    "password": "LSQiM7hoW7A3N7",
    "database": "cilantrodb"
}

db_config_another = {
    "host": "68.183.76.41",
    "port": "40601",
    "user": "cilantro_readonly",
    "password": "{2O7EAhSj>[Ksu^+bAcR",
    "database": "cilantro"
}

# Function to fetch table names
def fetch_table_names(db_config):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    table_names = [table[0] for table in cursor.fetchall()]
    cursor.close()
    connection.close()
    return table_names

#st.write(fetch_table_names(db_config_cilantro))
# Fetch table names for another database
#another_tables = fetch_table_names(db_config_another)
#st.title("Tables in another database:")
#st.write(another_tables)






# Function to fetch data based on the SQL query and date range
def fetch_data_for_date_range(start_date, end_date, db_config):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Construct the SQL query with the date range filter
    query = """
    SELECT 
    tbl_orders.cilantro_id, 
    tbl_vendor.name, 
    GROUP_CONCAT(CONCAT(tbl_orders_item.quantity, 'X ', tbl_general_products.name)), 
    tbl_main_subcategory.name AS main_subcategory_name,  -- Add this line to fetch subcategory name
    tbl_orders.payment_type, 
    tbl_orders.status, 
    tbl_orders.item_total_amount, 
    tbl_user.username, 
    tbl_user.phone, 
    tbl_user.email, 
    tbl_orders.estimated_datetime, 
    tbl_orders.confirm_datetime, 
    tbl_orders.prepared_datetime, 
    tbl_orders.picked_datetime, 
    tbl_promocode.promocode
FROM cilantrodb.tbl_orders
LEFT JOIN cilantrodb.tbl_user ON cilantrodb.tbl_orders.user_id = cilantrodb.tbl_user.id
LEFT JOIN cilantrodb.tbl_vendor ON cilantrodb.tbl_vendor.id = cilantrodb.tbl_orders.vendor_id
LEFT JOIN cilantrodb.tbl_promocode ON cilantrodb.tbl_promocode.id = cilantrodb.tbl_orders.promocode_id
LEFT JOIN cilantrodb.tbl_orders_item ON cilantrodb.tbl_orders_item.order_id = cilantrodb.tbl_orders.id
LEFT JOIN cilantrodb.tbl_products ON cilantrodb.tbl_orders_item.product_id = cilantrodb.tbl_products.id
LEFT JOIN cilantrodb.tbl_general_products ON cilantrodb.tbl_products.general_product_id = cilantrodb.tbl_general_products.id
LEFT JOIN cilantrodb.tbl_main_subcategory ON cilantrodb.tbl_general_products.mainsubcategory_id = cilantrodb.tbl_main_subcategory.id  -- Join with subcategory table
WHERE cilantrodb.tbl_orders.confirm_datetime BETWEEN %s AND %s
GROUP BY cilantrodb.tbl_orders.id
ORDER BY cilantrodb.tbl_orders.confirm_datetime ASC

    """

    cursor.execute(query, (start_date, end_date))
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data

# Streamlit UI
st.title("Sales Mix for the Selected Date Range")

# Date range input
start_date = st.date_input('Start Date')
end_date = st.date_input('End Date')

# Convert start and end dates to SQL-compatible format
start_date_sql = start_date.strftime('%Y-%m-%d')
end_date_sql = end_date.strftime('%Y-%m-%d')

# Call the function to fetch data for the selected date range
data = fetch_data_for_date_range(start_date_sql, end_date_sql, db_config_cilantro)

# Create sales mix from the fetched data
sales_mix = {}

for row in data:
    item_details = row[2]  # Assuming item details is in the third column
    subcategory_name = row[3]  # Assuming subcategory name is in the fourth column
    if item_details is not None:
        items = item_details.split(',')
        for item in items:
            quantity, name = item.strip().split('X')
            name = name.strip()
            quantity = int(quantity.strip())

            if name not in sales_mix:
                sales_mix[name] = {"Quantity": 0, "Subcategory": subcategory_name}  # Add subcategory to sales mix entry
            sales_mix[name]["Quantity"] += quantity

# Convert sales mix to DataFrame for display
sales_mix_df = pd.DataFrame(sales_mix.values(), index=sales_mix.keys())

st.set_option('deprecation.showPyplotGlobalUse', False)




# Display bar chart for items
st.subheader("Bar Chart for Item Sales")
st.bar_chart(sales_mix_df['Quantity'])

# Group sales mix by subcategory
subcategory_sales = sales_mix_df.groupby('Subcategory').sum()

# Display bar chart for subcategories
st.subheader("Bar Chart for Subcategory Sales")
st.bar_chart(subcategory_sales['Quantity'])

# Display bar chart for subcategories
st.subheader("Data table - Export if needed")
st.dataframe(sales_mix_df)
