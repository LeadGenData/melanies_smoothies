import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session

# 1. Title & Instruction
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# 2. Name on Order (The missing "Person" part)
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# 3. Get the Session & Data
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# 4. Ingredients Selection
ingredients_list = st.multiselect(
    'Select up to 5 ingredients:', 
    my_dataframe, 
    max_selections=5
)

# 5. Submission Logic
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    # Updated SQL to include BOTH the ingredients AND the name_on_order
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    if st.button('Submit Order'):
        # Only submit if a name is actually entered
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        else:
            st.error("Please enter a name before submitting.")
