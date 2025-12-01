import logging
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)
# models that will be used in project
try:
    # Set OpenAI API key
    load_dotenv("api_key")
    # generate slide points and explanation and translator
    llm = ChatOpenAI(temperature=0.8, model_name='gpt-3.5-turbo')

except Exception as e:
    logger.error(f"An error occurred: {e}")
