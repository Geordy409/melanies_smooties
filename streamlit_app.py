# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session  # ✅ IMPORT MANQUANT

# Write directly to the app.
st.title("🥤Customize Your Smoothie!🥤 ")
st.write(
    """
    Choose your fruits you want in your custom Smoothie.
    """
)

name_on_oder = st.text_input('Name on Smoothie:')
st.write('The name on the Smoothie will be:', name_on_oder)

# ✅ Snowflake session (OK uniquement dans Snowflake Streamlit)
session = get_active_session()

my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.to_pandas()['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_oder}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# External API
smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)
st.json(smoothiefroot_response.json())
