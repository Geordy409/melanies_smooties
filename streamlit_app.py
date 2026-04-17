# Import python packages
import streamlit as st
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# ----------------- Snowflake connection -----------------

connection_parameters = {
    "account": st.secrets["connections"]["snowflake"]["account"],
    "user": st.secrets["connections"]["snowflake"]["user"],
    "role": st.secrets["connections"]["snowflake"]["role"],
    "warehouse": st.secrets["connections"]["snowflake"]["warehouse"],
    "database": st.secrets["connections"]["snowflake"]["database"],
    "schema": st.secrets["connections"]["snowflake"]["schema"],
}

session = Session.builder.configs(connection_parameters).create()

# ----------------- Streamlit UI -----------------
st.title("🥤 Customize Your Smoothie! 🥤")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# ----------------- Fruits from Snowflake -----------------
fruit_df = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ----------------- Insert order -----------------
if ingredients_list and name_on_order:
    ingredients_string = " ".join(ingredients_list)

    insert_stmt = """
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES (?, ?)
    """

    if st.button("Submit Order"):
        session.sql(
            insert_stmt,
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success("✅ Your Smoothie is ordered!")

# ----------------- External API -----------------
response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)
st.json(response.json())
