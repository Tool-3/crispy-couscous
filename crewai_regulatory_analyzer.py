from crewai import Crew, Agent, Task
import requests  # For URL handling

# --- API Keys (Conceptual - Securely manage these in a real application) ---
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GOOGLE_AI_STUDIO_API_KEY = "YOUR_GOOGLE_AI_STUDIO_API_KEY"

# --- Helper Functions for API Calls (Conceptual) ---
def analyze_text_groq(text, instruction):
    """Conceptual function to call Groq API for text analysis."""
    return f"Analysis from Groq API for: {instruction} on text: '{text[:50]}...'"  # Placeholder

def analyze_text_google_ai_studio(text, instruction):
    """Conceptual function to call Google AI Studio API."""
    return f"Analysis from Google AI Studio API for: {instruction} on text: '{text[:50]}...'"  # Placeholder

# --- Agent Definitions ---
class RegulatoryParserAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Regulatory Document Parser',
            goal='Break down regulatory text into paragraphs for analysis.',
            backstory="Expert in parsing legal and regulatory documents to prepare them for AI analysis.",
            verbose=False,
            allow_delegation=True  # Corrected parameter name
        )

    def parse_document(self, document_content):
        """Parses the document content into paragraphs."""
        return [p.strip() for p in document_content.split('\n\n') if p.strip()]

class ActionItemAgent(Agent):
    def __init__(self, api_choice="groq"):
        super().__init__(
            role='Action Item Extractor',
            goal='Identify actionable items from each paragraph of regulatory text.',
            backstory="Experienced compliance officer skilled in identifying concrete actions required by regulations.",
            verbose=False,
            allow_delegation=True,
            api_choice=api_choice  # Store API choice as instance variable
        )

    def _execute(self, task):
        """Executes the task to extract action items using the selected API."""
        paragraph = task.input_data.get('paragraph', '')
        instruction = "Identify and list the actionable items in this regulatory paragraph."
        
        if self.api_choice == "groq":
            return analyze_text_groq(paragraph, instruction)
        elif self.api_choice == "google_ai":
            return analyze_text_google_ai_studio(paragraph, instruction)
        return "No API selected - Action Items Placeholder"

class RiskMitigationAgent(Agent):
    def __init__(self, api_choice="groq"):
        super().__init__(
            role='Risk Mitigation Strategist',
            goal='Suggest risk mitigation strategies for each actionable item in regulatory paragraphs.',
            backstory="Expert in risk management and regulatory compliance, capable of devising mitigation plans.",
            verbose=False,
            allow_delegation=False,
            api_choice=api_choice
        )

    def _execute(self, task):
        """Executes the task to suggest mitigations using the selected API."""
        paragraph = task.input_data.get('paragraph', '')
        actions = task.context[0].output if task.context else "No actions identified"
        instruction = f"Suggest risk mitigation strategies for: {actions}"
        
        if self.api_choice == "groq":
            return analyze_text_groq(paragraph, instruction)
        elif self.api_choice == "google_ai":
            return analyze_text_google_ai_studio(paragraph, instruction)
        return "No API selected - Mitigation Placeholder"

# --- Task Definitions ---
def create_tasks(parser_agent, action_agent, mitigation_agent, document_content):
    """Creates tasks for the crew with proper dependencies."""
    paragraphs = parser_agent.parse_document(document_content)
    tasks = []

    for idx, paragraph in enumerate(paragraphs):
        # Action item extraction task
        action_task = Task(
            description=f"Extract action items from paragraph {idx+1}",
            assignee=action_agent,
            input_data={'paragraph': paragraph},
            expected_output="List of actionable items from the regulatory paragraph."
        )
        
        # Risk mitigation task with dependency
        mitigation_task = Task(
            description=f"Suggest mitigations for paragraph {idx+1} actions",
            assignee=mitigation_agent,
            input_data={'paragraph': paragraph},
            context=[action_task],
            expected_output="Risk mitigation strategies for the identified action items."
        )
        
        tasks.extend([action_task, mitigation_task])
    
    return tasks

# --- Crew Orchestration ---
def create_regulatory_crew(api_choice_actions="groq", api_choice_mitigation="groq"):
    """Creates the crew with selected API providers."""
    parser_agent = RegulatoryParserAgent()
    action_agent = ActionItemAgent(api_choice=api_choice_actions)
    mitigation_agent = RiskMitigationAgent(api_choice=api_choice_mitigation)

    return Crew(
        agents=[parser_agent, action_agent, mitigation_agent],
        tasks=[],
        verbose=False
    )

# --- Execution Flow ---
def process_regulatory_obligation(input_type, input_source, api_actions="groq", api_mitigation="groq"):
    """Main processing function with proper task dependencies and result handling."""
    crew = create_regulatory_crew(api_actions, api_mitigation)
    
    # Document content loading
    document_content = ""
    if input_type == "url":
        try:
            response = requests.get(input_source)
            response.raise_for_status()
            document_content = response.text
        except Exception as e:
            return f"Error loading URL: {str(e)}"
    elif input_type == "file":
        document_content = input_source
    else:
        return "Invalid input type. Use 'url' or 'file'."

    if not document_content.strip():
        return "No valid document content found."

    # Create and execute tasks
    parser = RegulatoryParserAgent()
    crew.tasks = create_tasks(parser, 
                             crew.agents[1],  # Action agent
                             crew.agents[2],  # Mitigation agent
                             document_content)
    
    results = crew.kickoff()

    # Structure results
    output = {}
    paragraphs = parser.parse_document(document_content)
    for idx, para in enumerate(paragraphs):
        output[f"Paragraph {idx+1}"] = {
            "text": para,
            "actions": results[idx*2],
            "mitigations": results[idx*2+1]
        }
    
    return output
