import requests
import pandas as pd
import json
from datetime import datetime
import streamlit as st


def getData(adults,children,start_date,nights):
    end_date = pd.date_range(str(start_date), periods=nights+1).strftime('%Y-%m-%d').to_list()[-1]
    
    try:
        url = "https://cary.dbm.guestline.net/api/availabilities/CARY/CARYARMS?arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
        url_to_show = "https://cary.dbm.guestline.net/availability?hotel=CARYARMS&arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
        response = requests.get(url)
        data = json.loads(response.text)
        df = pd.json_normalize(data,record_path=['prices'],meta=['roomId','availability'])
 
    
        url_rooms = "https://cary.dbm.guestline.net/api/roomRates/CARY/CARYARMS?language=en"
        response_rooms = requests.get(url_rooms)
        data_rooms = json.loads(response_rooms.text)
        df_rooms = pd.json_normalize(data_rooms['rooms'])

        final_df = pd.merge(df,df_rooms[['name','id','occupancy.maxAdults','occupancy.maxChildren','occupancy.maxOverall']],how='left',left_on=['roomId'],right_on=['id'])
        final_df = final_df[['date','name','amountBeforeTax','availability','occupancy.maxAdults','occupancy.maxChildren','occupancy.maxOverall']]
        final_df.rename(columns = {'amountBeforeTax':'Price Per Day'}, inplace = True)
    except:
        st.write("There are no available data")
        return pd.DataFrame(),""
  

    return final_df,url_to_show

def getAllRooms():
    url_rooms = "https://cary.dbm.guestline.net/api/roomRates/CARY/CARYARMS?language=en"
    response_rooms = requests.get(url_rooms)
    data_rooms = json.loads(response_rooms.text)
    df_rooms = pd.json_normalize(data_rooms['rooms'])[['id','name','occupancy.maxAdults','occupancy.maxChildren','occupancy.maxOverall']]
    
    rooms_id = df_rooms['id'].to_list()
    rooms_name = df_rooms['name'].to_list()
    return df_rooms,rooms_id,rooms_name


def test(adults,children,start_date,nights,option):
  
    df_rooms,rooms_id,rooms_name = getAllRooms()
    index = rooms_name.index(option)
    room_id = rooms_id[index]

    end_date = pd.date_range(str(start_date), periods=nights+1).strftime('%Y-%m-%d').to_list()[-1]

    url = "https://cary.dbm.guestline.net/api/availabilities/CARY/CARYARMS?arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
    url_to_show = "https://cary.dbm.guestline.net/availability?hotel=CARYARMS&arrival=" + str(start_date) + "&departure=" + str(end_date) + "&adults=" + str(adults) + "&children=" + str(children)
    response = requests.get(url)
    data = json.loads(response.text)
    
    try:
        df = pd.json_normalize(data,record_path=['prices'],meta=['roomId','availability'])
        df.drop_duplicates(subset=['date','roomId'],inplace=True)
        final_df = pd.merge(df,df_rooms[['name','id','occupancy.maxAdults','occupancy.maxChildren','occupancy.maxOverall']],how='left',left_on=['roomId'],right_on=['id'])
        
        df_interested = final_df.loc[(final_df['roomId'] == room_id)]
        df_interested = df_interested[['date','name','amountBeforeTax','occupancy.maxAdults','occupancy.maxChildren','occupancy.maxOverall']]
        df_interested.rename(columns = {'amountBeforeTax':'Price Per Day'}, inplace = True)

        return df_interested,url_to_show

    except:
        st.write("There are no available data")
        return pd.DataFrame(),""
    

@st.cache
def convert_df(df):
   return df.to_csv().encode('utf-8')   


if __name__ == "__main__":
    option = st.sidebar.selectbox("Please select cottage: ", ('ALL','SEAVIEW COTTAGE NUMBER 7', 'Rose Cottage', 'Smugglers Cottage', 'Foxes Walk Cottage', 'Cove Cottage', 'Bay Cottage', 'Beach Cottage'))
    start_date = st.sidebar.date_input('Please enter arrival date: ')
    nights = st.sidebar.number_input('Please enter number of stays: ',step=1,min_value=1)
    adults=1
    children=0

    if option != 'ALL':
        st.header("Data for " + str(option))
        df_all,url = test(adults,children,start_date,nights,option)
        st.table(df_all)
        st.write("URL:" , url)
    
    else:
        st.header("Data for all cottages")
        df_all, url = getData(adults,children,start_date,nights)
        st.table(df_all)
        st.write("URL:" , url)

    csv = convert_df(df_all)

    st.download_button(
    "Download CSV",
    csv,
    "file.csv",
    "text/csv",
    key='download-csv'
    )

    
   

