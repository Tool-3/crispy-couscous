from crewai import Crew, Agent, Task
import requests  # For URL handling

# --- API Keys (Conceptual - Securely manage these in a real application) ---
# API keys should ideally be managed via Streamlit secrets or environment variables
# For simplicity, we'll keep placeholders here, but emphasize secure management in README
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GOOGLE_AI_STUDIO_API_KEY = "YOUR_GOOGLE_AI_STUDIO_API_KEY"

# --- Helper Functions for API Calls (Conceptual) ---
def analyze_text_groq(text, instruction):
    """Conceptual function to call Groq API for text analysis."""
    # Replace with actual Groq API call using their Python SDK or requests
    # Example (Conceptual - may not be actual Groq API format):
    # response = requests.post(
    #     "https://api.groq.com/...",
    #     headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
    #     json={"text": text, "instruction": instruction}
    # )
    # return response.json() # or response.text, depending on API output
    return f"Analysis from Groq API for: {instruction} on text: '{text[:50]}...'" # Placeholder

def analyze_text_google_ai_studio(text, instruction):
    """Conceptual function to call Google AI Studio API."""
    # Replace with actual Google AI Studio API call using their Python SDK or requests
    # Example (Conceptual - may not be actual Google AI Studio API format):
    # from google.generativeai import GenerativeModel
    # model = GenerativeModel("gemini-pro", api_key=GOOGLE_AI_STUDIO_API_KEY)
    # response = model.generate_content(f"{instruction} on text: {text}")
    # return response.text
    return f"Analysis from Google AI Studio API for: {instruction} on text: '{text[:50]}...'" # Placeholder


# --- Agent Definitions ---
class RegulatoryParserAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Regulatory Document Parser',
            goal='Break down regulatory text into paragraphs for analysis.',
            backstory="Expert in parsing legal and regulatory documents to prepare them for AI analysis.",
            verbose=False, # Set verbose to False for cleaner Streamlit output
            allow_delegation=True
        )

    def parse_document(self, document_content):
        """Parses the document content into paragraphs."""
        paragraphs = document_content.strip().split('\n\n') # Simple paragraph split - adjust based on document format
        return paragraphs

class ActionItemAgent(Agent):
    def __init__(self, api_choice="groq"): # Option to choose API
        super().__init__(
            role='Action Item Extractor',
            goal='Identify actionable items from each paragraph of regulatory text.',
            backstory="Experienced compliance officer skilled in identifying concrete actions required by regulations.",
            verbose=False, # Set verbose to False for cleaner Streamlit output
            allow_delegation=True
        )
        self.api_choice = api_choice

    def extract_actions(self, paragraph):
        """Extracts actionable items from a paragraph using selected API."""
        instruction = "Identify and list the actionable items in this regulatory paragraph."
        if self.api_choice == "groq":
            analysis_result = analyze_text_groq(paragraph, instruction)
        elif self.api_choice == "google_ai":
            analysis_result = analyze_text_google_ai_studio(paragraph, instruction)
        else:
            analysis_result = "No API selected - Action Items Placeholder" # Default if no API chosen
        return analysis_result # In real implementation, parse API result for actions

class RiskMitigationAgent(Agent):
    def __init__(self, api_choice="groq"): # Option to choose API
        super().__init__(
            role='Risk Mitigation Strategist',
            goal='Suggest risk mitigation strategies for each actionable item in regulatory paragraphs.',
            backstory="Expert in risk management and regulatory compliance, capable of devising mitigation plans.",
            verbose=False, # Set verbose to False for cleaner Streamlit output
            allow_delegation=False # No delegation for final mitigation suggestions
        )
        self.api_choice = api_choice

    def suggest_mitigations(self, paragraph, actionable_items):
        """Suggests risk mitigation strategies for actionable items using selected API."""
        instruction = f"For the regulatory paragraph: '{paragraph[:100]}...', and actionable items: '{actionable_items}', suggest risk mitigation strategies for each action."
        if self.api_choice == "groq":
            analysis_result = analyze_text_groq(paragraph, instruction)
        elif self.api_choice == "google_ai":
            analysis_result = analyze_text_google_ai_studio(paragraph, instruction)
        else:
            analysis_result = "No API selected - Mitigation Placeholder" # Default if no API chosen
        return analysis_result # In real implementation, parse API result for mitigations


# --- Task Definitions ---
def create_tasks(parser_agent, action_agent_groq, action_agent_google, mitigation_agent_groq, mitigation_agent_google, document_content):
    """Creates tasks for the crew based on document content."""
    paragraphs = parser_agent.parse_document(document_content)
    tasks = []

    for paragraph in paragraphs:
        # Task for Action Item Extraction (Groq API)
        task_actions_groq = Task(
            description=f"Extract actionable items from this regulatory paragraph: '{paragraph[:150]}...'",
            agent=action_agent_groq
        )
        tasks.append(task_actions_groq)

        # Task for Action Item Extraction (Google AI Studio API)
        task_actions_google = Task(
            description=f"Extract actionable items from this regulatory paragraph: '{paragraph[:150]}...'",
            agent=action_agent_google
        )
        tasks.append(task_actions_google)


        # Task for Risk Mitigation (Groq API) - Needs Actionable Items as Input (Conceptual)
        task_mitigation_groq = Task(
            description=f"Suggest risk mitigation strategies for the actionable items in this paragraph: '{paragraph[:150]}...'. Consider the actions identified previously.",
            agent=mitigation_agent_groq # In real implementation, task dependencies would be managed to pass actionable items
        )
        tasks.append(task_mitigation_groq)

        # Task for Risk Mitigation (Google AI Studio API) - Needs Actionable Items as Input (Conceptual)
        task_mitigation_google = Task(
            description=f"Suggest risk mitigation strategies for the actionable items in this paragraph: '{paragraph[:150]}...'. Consider the actions identified previously.",
            agent=mitigation_agent_google # In real implementation, task dependencies would be managed to pass actionable items
        )
        tasks.append(task_mitigation_google)
    return tasks


# --- Crew Orchestration ---
def create_regulatory_crew(api_choice_actions="groq", api_choice_mitigation="groq"): # Option to choose APIs for different agents
    """Creates the crew of agents."""
    parser_agent = RegulatoryParserAgent()
    action_agent_groq = ActionItemAgent(api_choice="groq")
    action_agent_google = ActionItemAgent(api_choice="google_ai")
    mitigation_agent_groq = RiskMitigationAgent(api_choice="groq")
    mitigation_agent_google = RiskMitigationAgent(api_choice="google_ai")


    crew = Crew(
        agents=[parser_agent, action_agent_groq, action_agent_google, mitigation_agent_groq, mitigation_agent_google],
        tasks=[], # Tasks are added dynamically based on input
        verbose=False # Set crew verbose to False for cleaner Streamlit output
    )
    return crew, parser_agent, action_agent_groq, action_agent_google, mitigation_agent_groq, mitigation_agent_google


# --- Input Handling and Execution ---
def process_regulatory_obligation(input_type, input_source, api_for_actions="groq", api_for_mitigation="groq"):
    """Main function to process regulatory obligation from URL or file."""
    crew, parser_agent, action_agent_groq, action_agent_google, mitigation_agent_groq, mitigation_agent_google = create_regulatory_crew(api_for_actions, api_for_mitigation)
    document_content = ""

    if input_type == "url":
        try:
            response = requests.get(input_source)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            document_content = response.text
        except requests.exceptions.RequestException as e:
            return f"Error fetching URL: {e}"
    elif input_type == "file":
        # --- File Upload Handling (Conceptual - Streamlit will handle file upload) ---
        document_content = input_source # input_source will be file content from Streamlit
    else:
        return "Invalid input type. Choose 'url' or 'file'."

    if not document_content:
        return "No document content to process."

    tasks = create_tasks(parser_agent, action_agent_groq, action_agent_google, mitigation_agent_groq, mitigation_agent_google, document_content)
    crew.tasks = tasks # Assign tasks to the crew

    results = crew.kickoff() # Run the crew to execute tasks

    # --- Output Structuring and Display ---
    hierarchical_output = {}
    paragraphs = parser_agent.parse_document(document_content)
    for i, paragraph in enumerate(paragraphs):
        hierarchical_output[f"Paragraph {i+1}"] = {
            "text": paragraph,
            "action_items_groq": results[i*4], # Access results based on task order
            "action_items_google_ai": results[i*4 + 1],
            "risk_mitigation_groq": results[i*4 + 2],
            "risk_mitigation_google_ai": results[i*4 + 3]
        }

    return hierarchical_output # Return hierarchical output for Streamlit to display
