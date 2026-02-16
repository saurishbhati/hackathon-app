import streamlit as st

def show_home():
    st.subheader("Welcome to Pathway AI")
    st.write("""
    Pathway AI is a multi-service platform aimed at assisting homeless individuals 
    with housing, resources, mental health support, and job assistance.  
    """)
    
    st.image("https://via.placeholder.com/800x300?text=Pathway+AI+Home+Banner", use_column_width=True)
    
    st.markdown("#### Key Features")
    st.write("- **Housing Matchmaker**: AI-powered shelter and low-income housing matching.")
    st.write("- **Resource Navigator**: Locate food banks, healthcare services, and more.")
    st.write("- **Mental Health Chatbot**: Access 24/7 crisis and emotional support.")
    st.write("- **Resume & Job Finder**: Generate professional resumes and explore opportunities.")
    st.write("- **Admin Dashboard**: View analytics and manage platform data.")

    st.markdown("---")
    st.write("Use the sidebar to explore different sections of the app.")

