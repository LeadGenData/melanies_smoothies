import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# --- TITLE & NAME ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')

# --- CONNECTION ---
cnx = st.connection("snowflake")
session = cnx.session()

# --- DATA PREP ---
# 1. Pull the data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# 2. Convert to Pandas so we can use loc() for easy lookup
pd_df = my_dataframe.to_pandas()

# --- SELECTION ---
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', 
    my_dataframe, 
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # 3. Look up the SEARCH_ON value for the current fruit (Image 3 logic)
        # Using .loc to find the row and .iloc[0] to grab the value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        # This sentence confirms the mapping is working (Image 2 logic)
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        # --- NUTRITION API CALL ---
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # --- SUBMIT ORDER ---
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
