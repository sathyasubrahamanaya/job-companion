from agno.os import AgentOS
from app.agents.agent import chat_agent



agent_os = AgentOS(agents=[chat_agent])
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main_os:app", reload=True)