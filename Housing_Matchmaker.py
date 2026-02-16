import streamlit as st
import geopy
from geopy.geocoders import Nominatim
import geopy.distance
import requests  # pip install requests
import openai  # pip install openai

# Initialize session state for storing map data if not already set
if "map_url" not in st.session_state:
    st.session_state["map_url"] = None
if "location_found" not in st.session_state:
    st.session_state["location_found"] = None

def show_housing_matchmaker():
    st.header("Shelter Finder Map")
    st.write("""
    Enter your general location (city or zip code) to view nearby homeless shelter locations on the map.
    """)
    
    location_input = st.text_input("Enter your current location (e.g., city or zip code)")
    family_size = st.number_input("Number of family members", min_value=1, max_value=20, value=1)
    
    if st.button("Find Housing"):
        if not location_input:
            st.error("Please enter a location.")
        else:
            # Geocode the provided location (approximate location)
            geolocator = Nominatim(user_agent="housing_matchmaker_app")
            location_data = geolocator.geocode(location_input)
            if not location_data:
                st.error("Could not determine your location. Please try a different input.")
                return
            
            user_lat = location_data.latitude
            user_lon = location_data.longitude
            st.session_state["location_found"] = location_data.address  # Save the found address
            
            # Build the Google Maps embed URL
            search_query = location_input.replace(" ", "+") + "+homeless+shelter"
            google_maps_api_key = "key"  # Replace with your valid API key
            map_url = f"https://www.google.com/maps/embed/v1/search?key={google_maps_api_key}&q={search_query}"
            st.session_state["map_url"] = map_url  # Save the embed URL
    
    # If a map has been generated, display it persistently.
    if st.session_state.get("map_url"):
        st.write("Location found: " + st.session_state.get("location_found", ""))
        st.markdown(
            f"""
            <iframe
                width="700"
                height="500"
                frameborder="0" style="border:0"
                src="{st.session_state.get('map_url')}" allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True
        )
    
    # ================================================================
    # Section 2: Shelter Analysis (Separate from Map)
    # ================================================================
    st.header("Shelter Analysis")
    st.write("""
    Enter your exact current address and the shelter address you'd like to analyze. 
    The system will calculate the distance between the two locations and provide additional details.
    """)
    
    with st.form("analysis_form"):
        current_exact_address = st.text_input("Enter your current exact address:")
        shelter_address = st.text_input("Enter the shelter address you'd like to analyze:")
        submit_button = st.form_submit_button("Analyze Shelter")
        
        if submit_button:
            if not current_exact_address or not shelter_address:
                st.error("Please enter both addresses.")
            else:
                # Use Nominatim to geocode addresses
                geolocator = Nominatim(user_agent="shelter_analysis_app")
                current_loc = geolocator.geocode(current_exact_address)
                shelter_loc = geolocator.geocode(shelter_address)
                
                if not current_loc:
                    st.error("Could not geocode your current address.")
                elif not shelter_loc:
                    st.error("Could not geocode the shelter address.")
                else:
                    # Get coordinates for both addresses
                    curr_lat, curr_lon = current_loc.latitude, current_loc.longitude
                    shelter_lat, shelter_lon = shelter_loc.latitude, shelter_loc.longitude

                    # Calculate the distance between the two addresses
                    distance_km = geopy.distance.distance((curr_lat, curr_lon), (shelter_lat, shelter_lon)).km

                    # Construct the prompt for GPT-4
                    prompt_message = (
                        f"User's current exact address: {current_exact_address} "
                        f"(coordinates: {curr_lat:.5f}, {curr_lon:.5f}).\n"
                        f"Shelter address: {shelter_address} "
                        f"(coordinates: {shelter_lat:.5f}, {shelter_lon:.5f}).\n"
                        f"Try to approximate the distance between the two locations without showing calculations.\n"
                        "Please provide details about how far apart the locations are along with additional helpful information such as accessibility, transit options, and nearby services."
                    )
                    
                    # Set your OpenAI API key (ensure you're using your valid key)
                    # openai.api_key should already be set above.
                    
                    try:
                        # Create the chat completion with streaming enabled
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You are an assistant that provides detailed analysis of shelter locations."},
                                {"role": "user", "content": prompt_message}
                            ],
                            temperature=0.7,
                            max_tokens=250,
                            stream=True
                        )
                        
                        # Use a Streamlit placeholder to update output as chunks arrive
                        output_placeholder = st.empty()
                        full_response = ""
                        
                        # Iterate synchronously over the streaming response
                        for chunk in response:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                full_response += delta["content"]
                                output_placeholder.markdown("### Shelter Analysis\n" + full_response)
                    
                    except Exception as e:
                        st.error(f"OpenAI API error: {e}")
                    
                    st.success("Shelter analysis complete!")

if __name__ == "__main__":
    show_housing_matchmaker()
