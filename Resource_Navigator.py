import streamlit as st
import requests
import openai
import folium
import geopy
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# Set your OpenAI API key
openai.api_key = "key"  # Replace with your actual OpenAI API key

# Use session_state to store the generated map and AI guidance so they persist on the page.
if "folium_map" not in st.session_state:
    st.session_state["folium_map"] = None
if "last_query" not in st.session_state:
    st.session_state["last_query"] = None
if "ai_guidance" not in st.session_state:
    st.session_state["ai_guidance"] = None

def show_resource_navigator():
    st.subheader("Resource Navigator")
    st.write("""
    Find food banks, healthcare facilities, emergency assistance, and job support near you.
    This page uses AI to suggest resources and guides you with an interactive map.
    Enter your address and describe what resources you need.
    """)

    # Resource type selection with an "Other" option
    resource_type = st.selectbox("Select Resource Type", 
                                 ["Food", "Healthcare", "Clothing", "Other"])

    # If "Other" is selected, prompt for a custom resource type.
    if resource_type == "Other":
        other_resource = st.text_input("Please specify the resource type", "")
        final_resource_type = other_resource.strip() if other_resource.strip() != "" else "Other"
    else:
        final_resource_type = resource_type

    # Text input for the address (for geocoding)
    address_input = st.text_input("Enter your address (city, zip code)", "")
    
    # Text input for what is needed (resource description)
    needs_description = st.text_input("Enter a description of what resources you need", "")

    # Button for triggering search
    if st.button("Search Resources"):
        final_address = address_input.strip()
        final_needs = needs_description.strip()
        
        if not final_address:
            st.error("Please provide your address.")
        elif not final_needs:
            st.error("Please provide what resources you need.")
        else:
            st.info(f"Searching {final_resource_type} listings near {final_address} with needs: {final_needs} ...")
            
            # Geocode the provided address
            geolocator = Nominatim(user_agent="resource_navigator_app")
            location_data = geolocator.geocode(final_address)
            if not location_data:
                st.error("Could not geocode your address. Please try a different input.")
                return

            user_lat = location_data.latitude
            user_lon = location_data.longitude

            # Construct a query string for the Google Places API:
            query = f"{final_resource_type} {final_needs} in {final_address}"
            google_maps_api_key = "AIzaSyATMJp_EqgFJyl8dTfc8A3Wt4hNriCwgV0"  # Replace with your valid API key
            places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query.replace(' ', '+')}&key={google_maps_api_key}"
            
            response = requests.get(places_url)
            if response.status_code != 200:
                st.error("Error retrieving data from Google Places API")
                return
            
            data = response.json()
            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                st.error("Google Places API returned error: " + data.get("status", "Unknown error"))
                return
            
            results = data.get("results", [])
            if not results:
                st.warning("No results found for the given query.")
            else:
                st.write(f"### {final_resource_type} Listings near {final_address}")
                # Create a Folium map centered on the user's location
                folium_map = folium.Map(location=[user_lat, user_lon], zoom_start=13)
                
                # Add a marker for the user's address
                folium.Marker(
                    location=[user_lat, user_lon],
                    popup="Your Location",
                    icon=folium.Icon(color="red", icon="user")
                ).add_to(folium_map)
                
                # Add markers for each resource found
                for result in results:
                    res_lat = result["geometry"]["location"]["lat"]
                    res_lon = result["geometry"]["location"]["lng"]
                    name = result.get("name", "Unknown")
                    addr = result.get("formatted_address", "Address not available")
                    folium.Marker(
                        location=[res_lat, res_lon],
                        popup=f"{name}\n{addr}",
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(folium_map)
                
                # Save the map and query in session_state so they persist on the page
                st.session_state["folium_map"] = folium_map
                st.session_state["last_query"] = query  # Save the query used
            
            # Provide AI-guided resource navigation using GPT-4 Turbo
            st.write("### AI Guidance")
            prompt = (
                f"Act as a resource navigator assistant. Given the resource type '{final_resource_type}', "
                f"the address '{final_address}', and the needs description '{final_needs}', "
                "provide a concise summary of how to access these services, suggest any additional support options, "
                "and highlight important considerations such as hours, eligibility, or contact information,"
                "Keep in mind that these ARE MEANT FOR HOMELESS people, so they must be specifically for them"
            )
            try:
                guidance_response = openai.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant specializing in resource navigation."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
                guidance = guidance_response.choices[0].message.content
                # Save the guidance in session_state so it persists
                st.session_state["ai_guidance"] = guidance
            except Exception as e:
                st.error("Error getting AI guidance: " + str(e))
    
    # Always display the persistent map if it exists
    if st.session_state["folium_map"] is not None:
        st.write("### Resource Map")
        st_folium(st.session_state["folium_map"], width=700, height=500)
    
    # Always display the persistent AI guidance if it exists
    if st.session_state["ai_guidance"] is not None:
        st.write("### AI Guidance")
        st.write(st.session_state["ai_guidance"])
    
    st.write("""
    **Future Enhancements**:
    - Integrate a more robust LangChain + FAISS semantic search for resource retrieval.
    - Continuously update service availability via a backend (FastAPI, MongoDB).
    - Expand voice input capabilities and improve transcription accuracy.
    """)

# To use this page, call show_resource_navigator() in your main Streamlit app.
