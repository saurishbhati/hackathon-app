import streamlit as st
from Home import show_home
from Housing_Matchmaker import show_housing_matchmaker
from Resource_Navigator import show_resource_navigator
from Mental_Health_Chatbot import show_mental_health_chatbot
from Resume_Job_Finder import get_businesses_for_job,create_business_map,show_app
from Admin_Dashboard import show_tutorial
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium



def main():
    st.set_page_config(page_title="Pathway AI: Smart Homeless Assistance Hub", layout="wide")

    # Create a sidebar for page navigation
    pages = {
        "Home": show_home,
        "Housing Matchmaker": show_housing_matchmaker,
        "Resource Navigator": show_resource_navigator,
        "Mental Health Chatbot": show_mental_health_chatbot,
        "Resume & Job Finder": show_app,
        "Tutorial": show_tutorial
    }

    # Sidebar selectbox
    page_selection = st.sidebar.selectbox("Go to page:", list(pages.keys()))
    
    # Call the selected page function
    pages[page_selection]()

if __name__ == "__main__":
    main()
