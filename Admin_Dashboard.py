import streamlit as st

def show_tutorial():
    st.subheader("Tutorial")
    st.write("""
    Welcome to the website tutorial! This guide will help you understand how to navigate the various pages on our site and make the most of the features available.

    Please keep in mind: Try to use capital letters or proper naming when necessary to help us give you the best responses possible!
    
    
    **1. Housing Matchmaker:**
    - **Purpose:** Find affordable and suitable housing options.
    - **How to Use:**  
      Enter your desired location and any additional preferences. The system will display an interactive map with available housing listings. Click on a marker for more details about the listing.
    - **Tips:**  
      Use the filters to narrow down your search. Hover over map markers to see quick details and click for a full description.

    **2. Resume & Job Finder:**
    - **Purpose:** Create a professional resume and get personalized job recommendations.
    - **How to Use:**  
      Input your skills, interests, and work experiences. Our AI will generate a resume in PDF format, which you can download. After that, you can generate a map where the system recommends job titles based on your profile and shows local businesses that may be hiring.
    - **Tips:**  
      Make sure to fill in all required fields. The recommended job titles help tailor the job search to your unique profile.

    **3. Resource Navigator:**
    - **Purpose:** Locate essential community resources such as food banks, healthcare services, emergency aid, and more.
    - **How to Use:**  
      Provide your address and the type of resources you need. An interactive map will display nearby services along with additional details.
    - **Tips:**  
      Check the resource details and directions to plan your visit.

    **4. Mental Health Chatbot:**
    - **Purpose:** Provide mental health support, guidance, and resources for those in need.
    - **How to Use:**  
      Chat with our mental health chatbot to receive supportive messages, coping strategies, and links to mental health resources. It is designed to help you manage stress, anxiety, and other mental health concerns.
    - **Tips:**  
      Remember, the chatbot is here to offer guidance and support, but it is not a substitute for professional help. If you are in crisis, please seek immediate assistance.

    **5. Tutorial Page (this page):**
    - **Purpose:** This page provides an overview and instructions for using the website.
    - **How to Use:**  
      Read through the descriptions for each section to understand the available features and how they can benefit you.
    - **Tips:**  
      Bookmark this page for quick reference. If you have any questions, use the "Need Career Advice?" section on the Resume & Job Finder page or contact support.

    **Additional Metrics and Future Enhancements:**
    - The website also includes performance metrics (such as active users, housing requests, and jobs found) to help you track trends.
    - We are continuously improving the platform with advanced analytics, enhanced resource mapping, and personalized recommendations.
    - Upcoming features include secure authentication, real-time data updates, and more interactive elements.

    We hope this tutorial helps you get started and make the most of our website. Enjoy exploring the features and let us know if you need any assistance!
    """)

if __name__ == "__main__":
    show_tutorial()
