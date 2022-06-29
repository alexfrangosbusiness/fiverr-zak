import requests
import pandas as pd
import json
from datetime import datetime
import streamlit as st


def getData(adults,children,start_date,nights):
    end_date = pd.date_range(str(start_date), periods=nights+1).strftime('%Y-%m-%d').to_list()[-1]
    
    url = "https://cary.dbm.guestline.net/api/availabilities/CARY/CARYARMS?arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
    url_to_show = "https://cary.dbm.guestline.net/availability?hotel=CARYARMS&arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
    response = requests.get(url)
    data = json.loads(response.text)
    df = pd.json_normalize(data,record_path=['prices'],meta=['roomId','availability'])

    url_rooms = "https://cary.dbm.guestline.net/api/roomRates/CARY/CARYARMS?language=en"
    response_rooms = requests.get(url_rooms)
    data_rooms = json.loads(response_rooms.text)
    df_rooms = pd.json_normalize(data_rooms['rooms'])

    final_df = pd.merge(df,df_rooms[['name','id']],how='left',left_on=['roomId'],right_on=['id'])
    final_df = final_df[['date','name','amountBeforeTax']]
    final_df.rename(columns = {'amountBeforeTax':'Price Per Day'}, inplace = True)


    return final_df,url_to_show

def getAllRooms():
    url_rooms = "https://cary.dbm.guestline.net/api/roomRates/CARY/CARYARMS?language=en"
    response_rooms = requests.get(url_rooms)
    data_rooms = json.loads(response_rooms.text)
    df_rooms = pd.json_normalize(data_rooms['rooms'])[['id','name']]

    rooms_id = df_rooms['id'].to_list()
    rooms_name = df_rooms['name'].to_list()
    return df_rooms,rooms_id,rooms_name


def test(adults,children,start_date,nights,option):
  
    df_rooms,rooms_id,rooms_name = getAllRooms()
    index = rooms_name.index(option)
    room_id = rooms_id[index]

    end_date = pd.date_range(str(start_date), periods=nights+1).strftime('%Y-%m-%d').to_list()[-1]
    print(end_date)

    url = "https://cary.dbm.guestline.net/api/availabilities/CARY/CARYARMS?arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
    url_to_show = "https://cary.dbm.guestline.net/availability?hotel=CARYARMS&arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
    response = requests.get(url)
    data = json.loads(response.text)
    
    try:
        df = pd.json_normalize(data,record_path=['prices'],meta=['roomId','availability'])
        df.drop_duplicates(subset=['date','roomId'],inplace=True)
        final_df = pd.merge(df,df_rooms[['name','id']],how='left',left_on=['roomId'],right_on=['id'])
        
        df_interested = final_df.loc[(final_df['roomId'] == room_id)]
        df_interested = df_interested[['date','name','amountBeforeTax']]
        df_interested.rename(columns = {'amountBeforeTax':'Price Per Day'}, inplace = True)

    except:
        st.write("There are no available data")
        return pd.DataFrame(),""
    
    return df_interested,url_to_show

@st.cache
def convert_df(df):
   return df.to_csv().encode('utf-8')   


if __name__ == "__main__":
    option = st.selectbox("Please select cottage: ", ('Luxury Double', 'SEAVIEW COTTAGE NUMBER 7', 'Captains Family Suite', 'Deluxe Double', 'Luxury Beach Hut', 'Rose Cottage', 'Smugglers Cottage', 'Foxes Walk Cottage', 'Cove Cottage', 'Pebble Suite', 'Bay Cottage', 'Shell Suite', 'Luxury Beach Suite', 'Beach Cottage'))
    start_date = st.date_input('Please enter arrival date: ')
    nights = st.number_input('Please enter number of stays: ',step=1,min_value=1)
    adults = st.number_input('Please enter number of adults: ',step=1,min_value=1)
    children = st.number_input('Please enter number of children: ', step=1)

    df,url = test(adults,children,start_date,nights,option)
    st.table(df)
    st.write("URL is:", url)
    
    csv = convert_df(df)

    st.download_button(
    "Download CSV",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv'
    )
