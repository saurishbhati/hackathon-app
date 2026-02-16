import streamlit as st
import geopy
from geopy.geocoders import Nominatim
import geopy.distance
import requests  # pip install requests
import openai  # pip install openai
import folium  # pip install folium
from streamlit_folium import st_folium  # pip install streamlit-folium

# Initialize session state for storing map data if not already set
if "folium_map" not in st.session_state:
    st.session_state["folium_map"] = None
if "location_found" not in st.session_state:
    st.session_state["location_found"] = None
if "shelter_count" not in st.session_state:
    st.session_state["shelter_count"] = 0


def show_housing_matchmaker():
    st.header("Shelter Finder Map")
    st.write(
        """
        Enter your general location (city or zip code) to view nearby homeless shelter locations on the map.
        """
    )

    location_input = st.text_input("Enter your current location (e.g., city or zip code)")
    family_size = st.number_input("Number of family members", min_value=1, max_value=20, value=1)

    if st.button("Find Housing"):
        if not location_input:
            st.error("Please enter a location.")
        else:
            # --- Geocode the provided location (fixes zip-only inputs mapping to the wrong country) ---
            query = location_input.strip()
            if query.isdigit() and len(query) == 5:
                query = f"{query}, United States"

            geolocator = Nominatim(user_agent="housing_matchmaker_app", timeout=10)
            location_data = geolocator.geocode(query, country_codes="us")

            if not location_data:
                st.error("Could not determine your location. Please try a different input (ex: '22033, VA').")
                return

            user_lat = location_data.latitude
            user_lon = location_data.longitude
            st.session_state["location_found"] = location_data.address

            # --- Find shelters nearby using OpenStreetMap (Overpass API) — no API key required ---
            radius_m = 8000  # 8km radius; adjust if needed
            overpass_query = f"""
            [out:json];
            (
              node(around:{radius_m},{user_lat},{user_lon})["amenity"="shelter"];
              way(around:{radius_m},{user_lat},{user_lon})["amenity"="shelter"];
              relation(around:{radius_m},{user_lat},{user_lon})["amenity"="shelter"];

              node(around:{radius_m},{user_lat},{user_lon})["social_facility"="shelter"];
              way(around:{radius_m},{user_lat},{user_lon})["social_facility"="shelter"];
              relation(around:{radius_m},{user_lat},{user_lon})["social_facility"="shelter"];

              node(around:{radius_m},{user_lat},{user_lon})["social_facility:for"="homeless"];
              way(around:{radius_m},{user_lat},{user_lon})["social_facility:for"="homeless"];
              relation(around:{radius_m},{user_lat},{user_lon})["social_facility:for"="homeless"];
            );
            out center;
            """

            try:
                r = requests.get(
                    "https://overpass-api.de/api/interpreter",
                    params={"data": overpass_query},
                    timeout=30,
                )
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                st.error(f"Could not load shelter data from OpenStreetMap. Error: {e}")
                return

            # --- Build map using OpenStreetMap tiles (no key) ---
            m = folium.Map(location=[user_lat, user_lon], zoom_start=12, tiles="OpenStreetMap")

            folium.Marker(
                [user_lat, user_lon],
                popup=folium.Popup("<b>Your location</b>", max_width=300),
            ).add_to(m)

            shelters_added = 0
            for el in data.get("elements", []):
                lat = el.get("lat") or (el.get("center") or {}).get("lat")
                lon = el.get("lon") or (el.get("center") or {}).get("lon")
                if lat is None or lon is None:
                    continue

                tags = el.get("tags", {}) or {}

                name = tags.get("name")
                operator_ = tags.get("operator")
                brand = tags.get("brand")
                street = tags.get("addr:street")
                housenumber = tags.get("addr:housenumber")
                city = tags.get("addr:city")
                phone = tags.get("phone") or tags.get("contact:phone")
                website = tags.get("website") or tags.get("contact:website")

                # Build a nicer title
                title = name or operator_ or brand or "Shelter"

                # Build a simple address line if available
                address_parts = []
                if housenumber:
                    address_parts.append(housenumber)
                if street:
                    address_parts.append(street)
                addr_line = " ".join(address_parts)

                details = []
                if addr_line:
                    details.append(addr_line)
                if city:
                    details.append(city)
                if phone:
                    details.append(f"Phone: {phone}")
                if website:
                    details.append(f"Website: {website}")

                popup_html = f"<b>{title}</b>"
                if details:
                    popup_html += "<br>" + "<br>".join(details)

                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                ).add_to(m)

                shelters_added += 1

            st.session_state["folium_map"] = m
            st.session_state["shelter_count"] = shelters_added

    # If a map has been generated, display it persistently.
    if st.session_state.get("folium_map"):
        st.write("Location found: " + st.session_state.get("location_found", ""))
        st.write(f"Shelters found nearby: {st.session_state.get('shelter_count', 0)}")
        st_folium(st.session_state["folium_map"], width=900, height=600)

    # ================================================================
    # Section 2: Shelter Analysis (Separate from Map)
    # ================================================================
    st.header("Shelter Analysis")
    st.write(
        """
        Enter your exact current address and the shelter address you'd like to analyze. 
        The system will calculate the distance between the two locations and provide additional details.
        """
    )

    with st.form("analysis_form"):
        current_exact_address = st.text_input("Enter your current exact address:")
        shelter_address = st.text_input("Enter the shelter address you'd like to analyze:")
        submit_button = st.form_submit_button("Analyze Shelter")

        if submit_button:
            if not current_exact_address or not shelter_address:
                st.error("Please enter both addresses.")
            else:
                # Use Nominatim to geocode addresses
                geolocator = Nominatim(user_agent="shelter_analysis_app", timeout=10)
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
                    distance_km = geopy.distance.distance(
                        (curr_lat, curr_lon), (shelter_lat, shelter_lon)
                    ).km

                    # Construct the prompt
                    prompt_message = (
                        f"User's current exact address: {current_exact_address} "
                        f"(coordinates: {curr_lat:.5f}, {curr_lon:.5f}).\n"
                        f"Shelter address: {shelter_address} "
                        f"(coordinates: {shelter_lat:.5f}, {shelter_lon:.5f}).\n"
                        f"Approximate distance: {distance_km:.1f} km.\n"
                        "Please provide helpful info such as accessibility, transit options, and nearby services."
                    )

                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an assistant that provides detailed analysis of shelter locations.",
                                },
                                {"role": "user", "content": prompt_message},
                            ],
                            temperature=0.7,
                            max_tokens=250,
                            stream=True,
                        )

                        output_placeholder = st.empty()
                        full_response = ""

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
