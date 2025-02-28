import streamlit as st
from crewai_regulatory_analyzer import process_regulatory_obligation

st.title("Regulatory Obligation Analyzer with CrewAI")

st.sidebar.header("Input Options")
input_type = st.sidebar.radio("Input Type", ["URL", "File Upload"])

input_source = None
document_content = None

if input_type == "URL":
    input_source = st.sidebar.text_input("Enter Regulatory Document URL:")
elif input_type == "File Upload":
    uploaded_file = st.sidebar.file_uploader("Upload Regulatory Document File", type=["txt", "pdf", "docx"]) # Add supported file types
    if uploaded_file is not None:
        # Read file content based on file type -  basic text file handling for now
        document_content = uploaded_file.read().decode("utf-8") # Assuming UTF-8 encoding for text files
        input_source = document_content # Pass document content directly


api_choice_actions = st.sidebar.selectbox("API for Action Item Extraction", ["groq", "google_ai"], index=0) # Default to Groq
api_choice_mitigation = st.sidebar.selectbox("API for Risk Mitigation", ["groq", "google_ai"], index=0) # Default to Groq


if st.sidebar.button("Analyze"):
    if not input_source:
        st.error("Please provide an input URL or upload a file.")
    else:
        st.info("Analyzing regulatory obligation...")
        if input_type == "URL":
            output = process_regulatory_obligation(input_type, input_source, api_choice_actions, api_choice_mitigation)
        elif input_type == "File Upload":
            output = process_regulatory_obligation(input_type, document_content, api_choice_actions, api_choice_mitigation) # Pass document_content

        if isinstance(output, dict):
            st.success("Analysis complete!")
            st.header("Analysis Results")
            for paragraph_key, paragraph_data in output.items():
                with st.expander(f"**{paragraph_key}:**"): # Use expander for each paragraph
                    st.subheader("Paragraph Text:")
                    st.write(paragraph_data['text'])
                    st.subheader("Action Items (Groq API):")
                    st.write(paragraph_data['action_items_groq'])
                    st.subheader("Action Items (Google AI Studio API):")
                    st.write(paragraph_data['action_items_google_ai'])
                    st.subheader("Risk Mitigation (Groq API):")
                    st.write(paragraph_data['risk_mitigation_groq'])
                    st.subheader("Risk Mitigation (Google AI Studio API):")
                    st.write(paragraph_data['risk_mitigation_google_ai'])
        else:
            st.error("Analysis failed or encountered an error:")
            st.write(output) # Display error message


st.sidebar.markdown("---")
st.sidebar.markdown("Powered by CrewAI, Groq API, and Google AI Studio API")
