import os
import asyncio
from crewai import Crew, Agent, Task
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import requests

# --- Helper Function to Initialize Google AI LLM ---
def get_google_llm():
    """Initialize Google AI LLM with proper async event loop handling."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-pro-exp-02-05",
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    finally:
        loop.close()

# --- Configure LLMs ---
groq_llm = ChatGroq(
    temperature=0.1,
    model="mixtral-8x7b-32768",
    groq_api_key=os.getenv("GROQ_API_KEY")  # From Streamlit secrets
)

google_llm = get_google_llm()

# --- Agent Definitions ---
class RegulatoryParserAgent(Agent):
    def __init__(self):
        super().__init__(
            role='Regulatory Document Parser',
            goal='Break down regulatory text into paragraphs for analysis.',
            backstory="Expert in parsing legal and regulatory documents.",
            verbose=False,
            allow_delegation=True,
            llm=groq_llm  # Default LLM for parsing
        )

    def parse_document(self, document_content):
        """Parse document content into paragraphs."""
        return [p.strip() for p in document_content.split('\n\n') if p.strip()]

class ActionItemAgent(Agent):
    def __init__(self, api_choice="groq"):
        llm = groq_llm if api_choice == "groq" else google_llm
        super().__init__(
            role='Action Item Extractor',
            goal='Identify actionable items from regulatory text.',
            backstory="Experienced compliance officer.",
            verbose=False,
            allow_delegation=True,
            llm=llm
        )

class RiskMitigationAgent(Agent):
    def __init__(self, api_choice="groq"):
        llm = groq_llm if api_choice == "groq" else google_llm
        super().__init__(
            role='Risk Mitigation Strategist',
            goal='Suggest risk mitigation strategies.',
            backstory="Expert in risk management.",
            verbose=False,
            llm=llm
        )

# --- Task Definitions ---
def create_tasks(parser_agent, action_agent, mitigation_agent, document_content):
    """Create tasks for the crew with proper dependencies."""
    paragraphs = parser_agent.parse_document(document_content)
    tasks = []

    for idx, paragraph in enumerate(paragraphs):
        # Action item extraction task
        action_task = Task(
            description=f"Extract action items from paragraph {idx+1}",
            agent=action_agent,
            expected_output="List of actionable items from the regulatory paragraph."
        )
        
        # Risk mitigation task with dependency
        mitigation_task = Task(
            description=f"Suggest mitigations for paragraph {idx+1} actions",
            agent=mitigation_agent,
            context=[action_task],
            expected_output="Risk mitigation strategies for the identified action items."
        )
        
        tasks.extend([action_task, mitigation_task])
    
    return tasks

# --- Crew Orchestration ---
def create_regulatory_crew(api_choice_actions="groq", api_choice_mitigation="groq"):
    """Create the crew with selected API providers."""
    parser_agent = RegulatoryParserAgent()
    action_agent = ActionItemAgent(api_choice=api_choice_actions)
    mitigation_agent = RiskMitigationAgent(api_choice=api_choice_mitigation)

    return Crew(
        agents=[parser_agent, action_agent, mitigation_agent],
        tasks=[],
        verbose=False
    )

# --- Main Processing Function ---
def process_regulatory_obligation(input_type, input_source, api_actions="groq", api_mitigation="groq"):
    """Process regulatory obligation from URL or file."""
    crew = create_regulatory_crew(api_actions, api_mitigation)
    
    # Load document content
    document_content = ""
    if input_type == "url":
        try:
            response = requests.get(input_source)
            response.raise_for_status()
            document_content = response.text
        except Exception as e:
            return f"Error loading URL: {str(e)}"
    elif input_type == "file upload":
        document_content = input_source
    else:
        return "Invalid input type. Use 'url' or 'file upload'."

    if not document_content.strip():
        return "No valid document content found."

    # Create and execute tasks
    parser = RegulatoryParserAgent()
    crew.tasks = create_tasks(parser, crew.agents[1], crew.agents[2], document_content)
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
