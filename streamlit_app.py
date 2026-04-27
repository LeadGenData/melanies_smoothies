# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# 1. Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# --- NEW: Get the Name for the Order ---
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get the session and data
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# 2. Multiselect widget
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe
    , max_selections=5
)

# 3. Only display if the list is NOT empty
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Updated SQL to include the new column: name_on_order
    # Note: Pay close attention to the single quotes and commas
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""
    
    # st.write(my_insert_stmt) # Uncomment if you need to debug for the badge
    
    # --- ADD THE SUBMIT BUTTON ---
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        # Adding the user's name to the success message for that extra touch
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")
