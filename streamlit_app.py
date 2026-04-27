import streamlit as st
from snowflake.snowpark.functions import col
import requests # Move all imports to the top

# --- TITLE & NAME ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')

# --- CONNECTION ---
cnx = st.connection("snowflake")
session = cnx.session()

# --- DATA & MULTISELECT ---
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
ingredients_list = st.multiselect('Select up to 5 ingredients:', my_dataframe, max_selections=5)

# --- THE REARRANGED DYNAMIC SECTION ---
if ingredients_list:
    ingredients_string = ''

    # We loop through each fruit the user picked
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Display nutrition for each fruit chosen
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # We replace the hardcoded "watermelon" with the fruit_chosen variable
        # Use a clean URL string (no brackets)
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        
        # Show the nutrition table for THIS fruit
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # --- SUBMIT ORDER SECTION ---
    # We move the button OUTSIDE the for-loop but INSIDE the if-statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
