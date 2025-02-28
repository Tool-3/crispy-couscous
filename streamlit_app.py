import streamlit as st
from crewai_regulatory_analyzer import process_regulatory_obligation

# Streamlit App Configuration
st.set_page_config(page_title="Regulatory Obligation Analyzer", page_icon="📜")

# App Title
st.title("📜 Regulatory Obligation Analyzer")
st.markdown("Analyze regulatory documents and extract actionable insights using AI.")

# Input Section
input_type = st.radio("Select Input Type", ["URL", "File Upload"])
input_source = None

if input_type == "URL":
    input_source = st.text_input("Enter Document URL")
elif input_type == "File Upload":
    uploaded_file = st.file_uploader("Upload Document", type=["txt", "pdf"])
    if uploaded_file:
        input_source = uploaded_file.read().decode("utf-8")

# API Selection
api_choice_actions = st.selectbox(
    "Select API for Action Item Extraction",
    ["groq", "google_ai"],
    index=0
)
api_choice_mitigation = st.selectbox(
    "Select API for Risk Mitigation",
    ["groq", "google_ai"],
    index=0
)

# Process Button
if st.button("Analyze Document"):
    if not input_source:
        st.error("Please provide a valid document URL or file.")
    else:
        with st.spinner("Analyzing document..."):
            try:
                output = process_regulatory_obligation(
                    input_type.lower(),
                    input_source,
                    api_choice_actions,
                    api_choice_mitigation
                )
                st.success("Analysis Complete!")
                st.json(output)  # Display results in JSON format
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
