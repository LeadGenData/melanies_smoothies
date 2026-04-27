import streamlit as st
from snowflake.snowpark.functions import col
import requests

# --- TITLE & NAME ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')

# --- CONNECTION ---
# Note: Use get_active_session() if running inside Snowflake, 
# or st.connection("snowflake") if running on Streamlit Cloud.
cnx = st.connection("snowflake")
session = cnx.session()

# --- DATA & MULTISELECT ---
# We bring in the SEARCH_ON column if your table has it, otherwise we clean it in Python
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True) # Optional: verify data

ingredients_list = st.multiselect(
    'Select up to 5 ingredients:', 
    my_dataframe, 
    max_selections=5
)

# --- THE DYNAMIC NUTRITION SECTION ---
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # CLEANING: Strip spaces so the API doesn't get confused
        search_on = fruit_chosen.strip().lower()
        
        st.subheader(search_on + ' Nutrition Information')
        
        # DYNAMIC API CALL
        try:
            smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
            
            # Check if the response contains the "not in database" error
            if "not in our database" in smoothiefroot_response.text:
                st.warning(f"Sorry, {search_on} nutrition info is currently unavailable.")
            else:
                st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        except Exception as e:
            st.error("Could not retrieve nutrition data at this time.")

    # --- SUBMIT ORDER SECTION ---
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        else:
            st.error("Please enter a name before submitting your order.")
