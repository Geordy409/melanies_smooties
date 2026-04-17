# Import python packages
import streamlit as st
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# ---------- Snowflake session handler ----------
def create_snowflake_session():
    try:
        # ✅ Cas Snowflake Streamlit
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        # ✅ Cas Streamlit Cloud
        connection_parameters = {
            "account": st.secrets["snowflake"]["account"],
            "user": st.secrets["snowflake"]["user"],
            "password": st.secrets["snowflake"]["password"],
            "role": st.secrets["snowflake"]["role"],
            "warehouse": st.secrets["snowflake"]["warehouse"],
            "database": st.secrets["snowflake"]["database"],
            "schema": st.secrets["snowflake"]["schema"],
        }
        return Session.builder.configs(connection_parameters).create()

session = create_snowflake_session()

# ---------- Streamlit UI ----------
st.title("🥤 Customize Your Smoothie! 🥤")

st.write("Choose your fruits you want in your custom Smoothie.")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

# ---------- Get fruits from Snowflake ----------
my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ---------- Insert order ----------
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

# ---------- External API ----------
response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.json(response.json())
