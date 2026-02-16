import streamlit as st
from fpdf import FPDF
import io
import openai
import requests
import json
import re
import time
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# Set your API keys (replace with your actual keys)
openai.api_key = "key"
google_maps_api_key = "key"

# Create a Nominatim geolocator with an increased timeout
geolocator = Nominatim(user_agent="job_finder_app", timeout=10)

def generate_resume(name, skills, interests, experiences):
    pdf = FPDF()
    pdf.add_page()

    # Use a placeholder if name is blank
    if not name.strip():
        name = "Candidate"

    # Header: Candidate's name and resume title
    pdf.set_font("Times", "B", 24)
    pdf.cell(0, 15, name, ln=True, align="C")
    pdf.set_font("Times", "", 16)
    pdf.cell(0, 10, "Curriculum Vitae", ln=True, align="C")
    pdf.ln(10)

    # Horizontal line
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # Section: Skills
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Skills", ln=True)
    pdf.ln(5)
    pdf.set_font("Times", "", 12)
    for skill in skills.split(","):
        clean_skill = skill.strip()
        if clean_skill:
            pdf.cell(10)
            pdf.cell(0, 10, f"- {clean_skill}", ln=True)
    pdf.ln(5)

    # Section: Interests
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Interests", ln=True)
    pdf.ln(5)
    pdf.set_font("Times", "", 12)
    for interest in interests.split(","):
        clean_interest = interest.strip()
        if clean_interest:
            pdf.cell(10)
            pdf.cell(0, 10, f"- {clean_interest}", ln=True)
    pdf.ln(5)

    # Section: Experiences
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 10, "Experiences", ln=True)
    pdf.ln(5)
    pdf.set_font("Times", "", 12)
    for experience in experiences.split("\n"):
        clean_experience = experience.strip()
        if clean_experience:
            pdf.cell(10)
            pdf.cell(0, 10, f"- {clean_experience}", ln=True)
    pdf.ln(5)

    # Get PDF output; if it's a string, encode it, otherwise assume it's already bytes.
    pdf_output = pdf.output(dest="S")
    pdf_bytes = pdf_output.encode("latin1") if isinstance(pdf_output, str) else pdf_output
    return io.BytesIO(pdf_bytes)

def get_recommended_job_types(skills, interests, experiences):
    prompt = (
        "Based on the following user profile, suggest one or two job titles that would best fit the user:\n\n"
        f"Skills: {skills}\n"
        f"Interests: {interests}\n"
        f"Experiences: {experiences}\n\n"
        "Return your answer as a short, comma-separated string (for example: 'Data Analyst, Business Intelligence Specialist')."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=50
        )
        answer = response.choices[0].message.content.strip()
        answer = re.sub(r"^```(?:\w+)?", "", answer)
        answer = re.sub(r"```$", "", answer).strip()
        return answer
    except Exception as e:
        st.error("Error getting recommended job types: " + str(e))
        return None

def get_businesses_for_job(job_query, location, retries=3, delay=5):
    query = f"{job_query} in {location}"
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query.replace(' ', '+')}&key={google_maps_api_key}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("status") == "OK":
                return data.get("results", [])
            else:
                st.error(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")
                return None
        except Exception as e:
            if "502" in str(e):
                st.warning(f"Received 502 error from Google API. Retrying in {delay} seconds... (Attempt {attempt + 1} of {retries})")
                time.sleep(delay)
            else:
                st.error("Error calling Google Places API: " + str(e))
                return None
    st.error("Failed to get data from Google Places API after multiple attempts.")
    return None

def create_business_map(businesses, location):
    center_loc = geolocator.geocode(location)
    if not center_loc:
        st.error("Unable to geocode your location. Please check your input.")
        return None

    # Create a map centered on the user's location with control_scale enabled
    m = folium.Map(
        location=[center_loc.latitude, center_loc.longitude],
        zoom_start=13,
        control_scale=True
    )
    
    # Mark the user's location
    folium.Marker(
        location=[center_loc.latitude, center_loc.longitude],
        popup="Your Location",
        icon=folium.Icon(color="red", icon="user")
    ).add_to(m)

    for business in businesses:
        address = business.get("formatted_address") or business.get("vicinity")
        name = business.get("name")
        if address:
            loc = geolocator.geocode(address)
            if loc:
                popup_text = f"{name}<br>{address}"
                folium.Marker(
                    location=[loc.latitude, loc.longitude],
                    popup=popup_text,
                    icon=folium.Icon(color="blue", icon="briefcase")
                ).add_to(m)
    return m

def answer_question(question):
    prompt = (
        "You are a helpful career advisor. Answer the following question regarding job interviews, "
        "skill development, or employment assistance:\n\n"
        f"{question}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful career advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error("Error getting answer: " + str(e))
        return None

# Initialize session state keys using .get() with a default value
if st.session_state.get('pdf_buffer', None) is None:
    st.session_state['pdf_buffer'] = None
if st.session_state.get('recommended_jobs', None) is None:
    st.session_state['recommended_jobs'] = None
if st.session_state.get('business_map', None) is None:
    st.session_state['business_map'] = None
if st.session_state.get('career_answer', None) is None:
    st.session_state['career_answer'] = None
if st.session_state.get('generated', None) is None:
    st.session_state['generated'] = False

def show_app():
    st.markdown("<h2 style='text-align: center;'>Job Opportunity Finder</h2>", unsafe_allow_html=True)
    st.write("Enter your **skills**, **interests**, **experiences**, and **location** below. "
             "We'll use AI to recommend job titles and then search for local businesses where you might apply.")

    # Input fields (name is optional; used only for resume)
    name = st.text_input("Full Name (optional for resume)")
    skills = st.text_area("Enter your skills (separated by commas)")
    interests = st.text_area("Enter your interests (separated by commas)")
    experiences = st.text_area("Enter your experiences (each on a new line)")
    location = st.text_input("Enter your location (City, State or Zip)")

    # Generation button - label changes based on session state
    button_label = "Generate Resume & Opportunities" if not st.session_state.get('generated', False) else "Generate Map"
    if st.button(button_label, key="gen_button"):
        if not (skills and interests and experiences and location):
            st.error("Please fill in all the fields except Full Name (which is optional).")
        else:
            st.session_state['generated'] = True  # Mark as generated so button label changes

            # Only generate new resume if not already generated
            if st.session_state.get('pdf_buffer') is None:
                st.session_state['pdf_buffer'] = generate_resume(name, skills, interests, experiences)
            st.success("Your AI-generated resume is ready!")
            st.download_button("Download Resume", data=st.session_state['pdf_buffer'], file_name="resume.pdf", mime="application/pdf", key="download_resume")
            
            if st.session_state.get('recommended_jobs') is None:
                recommended_jobs = get_recommended_job_types(skills, interests, experiences)
                if recommended_jobs:
                    st.session_state['recommended_jobs'] = recommended_jobs
                    st.success(f"Recommended Job Titles: {recommended_jobs}")
                else:
                    st.error("Could not determine recommended job titles. Please try again.")
            
            if st.session_state.get('recommended_jobs') and st.session_state.get('business_map') is None:
                businesses = get_businesses_for_job(st.session_state['recommended_jobs'], location)
                if not businesses:
                    st.warning("No businesses found for the recommended job titles. Using generic job search...")
                    businesses = get_businesses_for_job("jobs", location)
                if businesses:
                    business_map = create_business_map(businesses, location)
                    if business_map:
                        st.session_state['business_map'] = business_map
                        st.markdown("<h3 style='text-align: center;'>Local Job Opportunities Map</h3>", unsafe_allow_html=True)
                        st_folium(business_map, width=700, height=500)
                else:
                    st.error("No local businesses found. Please try a different location or check your API keys.")

    # Persist previously generated content
    if st.session_state.get('pdf_buffer'):
        st.download_button("Download Resume (Previously Generated)", data=st.session_state['pdf_buffer'], file_name="resume.pdf", mime="application/pdf", key="download_resume_prev")
    if st.session_state.get('recommended_jobs'):
        st.markdown(f"<h3 style='text-align: center;'>Recommended Job Titles: {st.session_state['recommended_jobs']}</h3>", unsafe_allow_html=True)
    if st.session_state.get('business_map'):
        st.markdown("<h3 style='text-align: center;'>Local Job Opportunities Map</h3>", unsafe_allow_html=True)
        st_folium(st.session_state['business_map'], width=700, height=500)
    
    # Career assistance Q&A section (placed below the generation button)
    st.markdown("<h3 style='text-align: center;'>Need Career Advice?</h3>", unsafe_allow_html=True)
    question = st.text_area("Ask a question about job interviews, skill development, or employment assistance:")
    if st.button("Get Answer"):
        if not question.strip():
            st.error("Please enter a question.")
        else:
            answer = answer_question(question)
            if answer:
                st.session_state['career_answer'] = answer
                st.markdown("<h4>Answer:</h4>", unsafe_allow_html=True)
                st.write(answer)
    
    if st.session_state.get('career_answer'):
        st.markdown("<h4>Previously Generated Answer:</h4>", unsafe_allow_html=True)
        st.write(st.session_state['career_answer'])

if __name__ == "__main__":
    show_app()
