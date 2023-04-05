import time
from datetime import date

import requests
import json
import streamlit as st
from streamlit_folium import folium_static
import folium

API_KEY = "131789df-fd43-45ec-b9b8-4ade681d23cc"
#TEST
@st.cache_data
def map_creator(latitude, longitude):
    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # add marker for the station
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)

@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={API_KEY}"
    countries_dict = requests.get(countries_url).json()
    # st.write(countries_dict)
    return countries_dict

@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={API_KEY}"
    states_dict = requests.get(states_url).json()
    # st.write(states_dict)
    return states_dict

@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={API_KEY}"
    cities_dict = requests.get(cities_url).json()
    # st.write(cities_dict)
    return cities_dict


def save_to_file(data, file_name):
    with open(file_name, "w") as write_file:
        json.dump(data, write_file, indent=2)
        print("You successfully saved to {}.".format(file_name))


st.title("Lab 2")
st.header("Air Quality Index")

preference = st.sidebar.selectbox("How would you like to choose location",
                                  options=["", "Country/State/City", "Nearest City", "Latitude/Longitude"])

if preference == "Country/State/City":
    countrys = requests.get(f'http://api.airvisual.com/v2/countries?key={API_KEY}').json()

    while countrys['status'] == "fail":
        warning = st.warning("Too Many Requests please wait")
        warning.empty()
        time.sleep(10)
        countrys = requests.get(f'http://api.airvisual.com/v2/countries?key={API_KEY}').json()

    countryNames = (list(map(lambda c: c['country'], countrys['data'])))

    countryNames.insert(0, ' ')

    #print(countryNames)

    country = st.selectbox("Select a Country", options=(countryNames))

    if country != ' ':
        states = requests.get(f'http://api.airvisual.com/v2/states?country={country}&key={API_KEY}').json()

        while states['status'] == "fail":
            warning = st.warning("Too Many Requests please wait")
            time.sleep(10)
            warning.empty()
            states = requests.get(f'http://api.airvisual.com/v2/states?country={country}&key={API_KEY}').json()

        stateNames = ([s['state'] for s in states['data']])
        stateNames.insert(0, ' ')
        state = st.selectbox("Select a State", options=stateNames)

        if state != ' ':

            citys = requests.get(
                f"http://api.airvisual.com/v2/cities?state={state}&country={country}&key={API_KEY}").json()

            while citys['status'] == "fail":
                warning = st.warning("Too Many Requests please wait")
                time.sleep(10)
                warning.empty()
                citys = requests.get(
                    f"http://api.airvisual.com/v2/cities?state={state}&country={country}&key={API_KEY}").json()

            cityNames = [c['city'] for c in citys['data']]
            city = st.selectbox("Select a City", options=cityNames)

            airQualityData = requests.get(
                f"https://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={API_KEY}").json()

            while airQualityData['status'] == "fail":
                warning = st.warning("Too Many Requests please wait")
                time.sleep(10)
                warning.empty()
                airQualityData = requests.get(
                    f"https://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={API_KEY}").json()

            map_creator(airQualityData["data"]["location"]["coordinates"][1],
                        airQualityData["data"]["location"]["coordinates"][0])

            today = date.today()
            st.markdown(f"<span style='color:lightBlue'>Today's date: {today}</span>", unsafe_allow_html=True)

            tempC = airQualityData["data"]["current"]["weather"]["tp"]
            tempF = (tempC * 1.8) + 32
            st.info(f"Tempature in miami is {tempC}°C/{tempF}°F")

            humidity = airQualityData["data"]["current"]["weather"]["hu"]
            st.info(f"Humidity is {humidity}%")

            airQuality = airQualityData["data"]["current"]["pollution"]["aqius"]
            st.info(f"The air quality index is currently {airQuality}")

if preference == "Nearest City":
    airQualityData = requests.get(f"http://api.airvisual.com/v2/nearest_city?key={API_KEY}").json()

    while airQualityData['status'] == "fail":
        warning = st.warning("Too Many Requests please wait")
        time.sleep(10)
        warning.empty()
        airQualityData = requests.get(f"http://api.airvisual.com/v2/nearest_city?key={API_KEY}").json()

    map_creator(airQualityData["data"]["location"]["coordinates"][1],
                airQualityData["data"]["location"]["coordinates"][0])

    today = date.today()
    st.markdown(f"<span style='color:lightBlue'>Today's date: {today}</span>", unsafe_allow_html=True)

    tempC = airQualityData["data"]["current"]["weather"]["tp"]
    tempF = (tempC * 1.8) + 32
    st.info(f"Tempature in miami is {tempC}°C/{tempF}°F")

    humidity = airQualityData["data"]["current"]["weather"]["hu"]
    st.info(f"Humidity is {humidity}%")

    airQuality = airQualityData["data"]["current"]["pollution"]["aqius"]
    st.info(f"The air quality index is currently {airQuality}")

if preference == "Latitude/Longitude":

   # while (True):
    longitude = st.number_input("Enter Your Longitude")
    latitude = st.number_input("Enter Your Latitude")

    submit = st.button("Submit")

    if submit:
        airQualityData = requests.get(
            f"http://api.airvisual.com/v2/nearest_city?lat={(latitude)}&lon={(longitude)}&key={API_KEY}").json()
        save_to_file(airQualityData, "t2.json")

        while airQualityData['status'] == "fail":

            tlat = latitude
            tlong = longitude

            warning = st.warning("Invalid Coordinates, please use another one")

            while not submit:
                submit = st.button("Resubmit")

            if tlat == latitude and tlong == longitude:
                warning = st.warning("Please use another coordinate ")

            warning.empty()

            airQualityData = requests.get(
                f"http://api.airvisual.com/v2/nearest_city?lat={(latitude)}&lon={(longitude)}&key={API_KEY}").json()
            save_to_file(airQualityData, "t2.json")
            warning.empty()



        map_creator(airQualityData["data"]["location"]["coordinates"][1],
                    airQualityData["data"]["location"]["coordinates"][0])

        today = date.today()
        st.markdown(f"<span style='color:lightBlue'>Today's date: {today}</br>"
                    f"Data taken from weather station in {airQualityData['data']['city']},"
                    f"{airQualityData['data']['country']}</span>", unsafe_allow_html=True)

        tempC = airQualityData["data"]["current"]["weather"]["tp"]
        tempF = (tempC * 1.8) + 32
        st.info(f"Tempature in miami is {tempC}°C/{tempF}°F")

        humidity = airQualityData["data"]["current"]["weather"]["hu"]
        st.info(f"Humidity is {humidity}%")

        airQuality = airQualityData["data"]["current"]["pollution"]["aqius"]
        st.info(f"The air quality index is currently {airQuality}")

            #submit = False
            #while (submit == False):
               # pass






