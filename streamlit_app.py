# Import python packages.
import streamlit as st
import pandas as pd
import requests 
from snowflake.snowpark.functions import col


# Write directly to the app.
st.title("🥤Customize Your Smoothie!🥤 ")
st.write(
  """
  Choose your fruits you want in your custom Smoothie.
  """)
name_on_oder = st.text_input('Name on Smoothie:')
st.write('The name on the Smoothie will be:', name_on_oder)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# convert to snowspark dataframe to a pandas dataframe so we can use the loc function

pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections = 5
)
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
      
        ingredients_string += fruit_chosen + " "
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/{search_on}" 
        )

        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    #st.write(ingredients_string)

    #my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_oder)
                    #values ('""" + ingredients_string + """','"""+name_on_oder+"""')"""
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_oder}')
            """

    #st.write(my_insert_stmt)
    #st.stop()
 
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success('Your Smoothie is ordered!', icon="✅")
      


    
