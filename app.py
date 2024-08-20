import streamlit as st
import pandas as pd
from pymongo.mongo_client import MongoClient



st.set_page_config(page_title='Web Scrapper',page_icon='https://img.icons8.com/?size=100&id=1349&format=png&color=000000', layout='wide', initial_sidebar_state="collapsed")

client = MongoClient(st.secrets['DBURL'])

collectionName = 'All_Websites'
database = client.WebScrapping
table = database[collectionName]

def load_csv():
    data = pd.read_csv(r'ScrappedFiles\{}.csv'.format(collectionName)) #File Load to pandas
    data_dict = data.to_dict(orient='records') # Data coverted to dictionary
    return data_dict
@st.cache_data
def Get_data_from_db():
    if collectionName in database.list_collection_names():
        fields_to_include = {'_id': 0, 
                            #   'Sub_Product': 0, 'RegularPrice': 0
                        }
        df = table.find({}, fields_to_include)
        df = pd.DataFrame(list(df))
        df['SalePrice'] = df['SalePrice'].replace(r'[\$,]', '', regex=True).astype(float)
        df['Rating'] = df['Rating'].astype(float)
        return df
    else:
        st.warning(f"Collection '{collectionName}' not exists. Please update your new data to Database....")

def csv_to_DB(collectionName, database,table):
    if collectionName in database.list_collection_names():
        st.warning(f"Collection '{collectionName}' already exists. We are updating your new data to Database....")
        database[collectionName].drop()
        st.success(f"Old Collection '{collectionName}' dropped.")
    bar = st.progress(0, text='Sending updated data to database🛢')
    table.insert_many(load_csv())
    bar.progress(100, text='Data Successfully sent')
    

left,center,right = st.columns([1,3,1])


center.markdown("""<h1 style= "text-align:center; ">Competitor Websites</h1>
""", unsafe_allow_html=True)



#########################################################################################################
st.markdown("***")
df = Get_data_from_db()
filtered_df = df
st.markdown("""<h3 style='text-align: center;'>Filters</h3>""", unsafe_allow_html=True)
Filter_A,Filter_B,Filter_C = st.columns([3,1,3])
Brand = Filter_A.multiselect('Brand', filtered_df['Brand'].unique(), default=['HarrisSeeds'])
U_ProductName = Filter_C.text_input('Enter Product Name : ')
min_rating, max_rating = Filter_A.select_slider(
    'Select a range of Ratings',
    options=[0, 1, 2, 3, 4, 5],
    value=(0, 4)  # default range
)
stock = Filter_C.multiselect('Availability', filtered_df['Availability'].unique())
min_price = Filter_A.text_input('Min Price')
max_price = Filter_C.text_input('Max Price')
if min_price:
    try:
        min_price = float(min_price) 
    except ValueError as e:
        st.error('Please enter numerics only')
if max_price:
    try:
        max_price = float(max_price) 
    except ValueError as e:
        st.error('Please enter numerics only')
Columns = st.multiselect('Select Columns you want to see' , filtered_df.keys(), default=['Brand', 'ProductName', 'SalePrice'])
#########################################################################################################
st.markdown("***")
if U_ProductName:
    filtered_df = df[df['ProductName'].str.contains(U_ProductName, case=False, regex=False)]
if Brand:
    filtered_df = filtered_df[filtered_df['Brand'].isin(Brand)]
if stock:
    filtered_df = filtered_df[filtered_df['Availability'].isin(stock)]
if min_rating and max_rating:
    filtered_df = filtered_df[(filtered_df['Rating'] >= min_rating) & (filtered_df['Rating'] <= max_rating)]
if min_price and max_price:
    filtered_df = filtered_df[(filtered_df['SalePrice'] >= min_price) & (filtered_df['SalePrice'] <= max_price)]

st.dataframe(filtered_df[Columns], hide_index=True,width=1200,
             column_config={
                 "ProductURL": st.column_config.LinkColumn("ProductURL"),  
             })