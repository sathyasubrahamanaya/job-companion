from agno.agent import Agent
from agno.models.google import Gemini
from app.config import settings
from app.agents import prompts

from app.schemas.models import CandidateProfile



model = Gemini(id=settings.GEMINI_MODEL_NAME
               ,api_key=settings.GEMINI_API_KEY)



user_name = "Adithya"
user_age = "20"
agent_role ="resume analyzer"
function_requirements = f""" 
1. you need analyze the resume and extract these details and provide in json format
2. dont provide any extra informations JSON  format only
3. {CandidateProfile.model_json_schema()}
4. No tools provided now

"""
agent_role = "Your Name is jobby. you work as resume analyzer." \
" your job is to analyze the candidate profile and extract information"

chat_agent = Agent(name=prompts.agent_name,
                   description=agent_role,
                   model=model,
                   instructions= prompts.inject_sp_resume_analyzer(agent_role,user_name,user_age,agent_role,function_requirements,"None at the moment"),
             )






