from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
   GROQ_API_KEY :str 
   GEMINI_API_KEY:str
   GEMINI_MODEL_NAME:str
   GROQ_MODEL_NAME:str
   VERSION:int

   model_config = SettingsConfigDict(
      env_file=".env",
      case_sensitive=False,
      env_file_encoding="utf-8"
   )

settings = Settings()
   