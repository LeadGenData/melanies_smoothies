import streamlit as st
from snowflake.snowpark.functions import col

# --- TITLE & NAME ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')

# --- THE FIX FOR LINE 14 ---
# Instead of get_active_session(), use the connection helper
cnx = st.connection("snowflake")
session = cnx.session()

# --- DATA & MULTISELECT ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect('Select up to 5 ingredients:', my_dataframe, max_selections=5)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

# New section to display smoothiefroot nutrition information
import requests  
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())
