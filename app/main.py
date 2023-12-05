import os
from time import sleep
from packaging import version
from fastapi import FastAPI, Request, HTTPException
import openai
from openai import OpenAI
import functions
import yaml
import logging
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('~~~~~~~~~~~~~~~~~LOGGING TES7 ~~~~~~~~~~~~~~~~~~')
print("~~~~~~~~~~~~PRINT TEST~~~~~~~~~~")


def load_api_key(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        return config['api_key']


#print(api_key) 
logger.info("####### printing env variables")
for key, value in os.environ.items():
    logger.info(f"{key}: {value}")

# Function to get environment variable
def get_api_key():

    api_key = os.getenv('API_KEY')
    if api_key is None:
        raise ValueError("API_KEY environment variable is not set.")
    return api_key

# Main code
try:
    OPENAI_API_KEY = get_api_key() # # #this gets it from the docker-compose    #load_api_key('cfg.yaml')
    # Use api_key in your application
except ValueError as e:
    logger.info(f"Error: {e}")
    # Handle the error (e.g., exit the program, log the error, etc.)

# Check OpenAI version is correct
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
#OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  logger.info("OpenAI version is compatible.")

# Start app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Init client
client = OpenAI(
    api_key=OPENAI_API_KEY)  # should use env variable OPENAI_API_KEY in secrets (bottom left corner)

# Create new assistant or load existing
assistant_id = functions.create_assistant(client)

#test
@app.get('/test')
async def test():
    logger.info("test...")
    return "test complete"

#start
@app.get('/start')
async def start_conversation():
    logger.info("Starting a new conversation...")
    thread = client.beta.threads.create()
    logger.info(f"New thread created with ID: {thread.id}")
    return {"thread_id": thread.id}

#chat
@app.post('/chat')
async def chat(request: Request):
    data = await request.json()
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')
    # Rest of your code

    if not thread_id:
        logger.info("Error: Missing thread_id")  # Debugging line
        return {"error": "Missing thread_id"}, 400

    logger.info(f"Received message: {user_input} for thread ID: {thread_id}"
            )  # Debugging line

  # Add the user's message to the thread
    client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  # Run the Assistant
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)

  # Check if the Run requires action (function call)
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                    run_id=run.id)
        logger.info(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            break
        sleep(1)  # Wait for a second before checking again

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    logger.info(f"Assistant response: {response}")  # Debugging line
    return {"response": response}
