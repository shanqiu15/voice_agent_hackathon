This project is an AI-powered audio customer service agent designed to handle Apple product support. The agent can perform tasks like scheduling repairs, canceling subscriptions, and answering product-related queries, while intelligently refusing to respond to requests for non-existent products. We utilize GPT-4 for orchestrating problem-solving, enabling the agent to guide users through complex interactions in a real-world simulation. This tool aims to streamline customer service for Apple by automating routine support tasks through natural language interactions.

We mocked the API/tool logic in this project because we don't have the real API access but you can easily replace them with real APIs. 

### Environment setup:
```
python -m venv .venv
source .venv/bin/activate
pip install pipcat-ai
pip install "pipecat-ai[daily,openai]"
pip install "pipecat-ai[cartesia]"
pip install python-dotenv
pip install pyaudio

cd voice_agent_hackathon
```
create .env file and add the following environment variables:
```
OPENAI_API_KEY=...
DAILY_SAMPLE_ROOM_URL=...
DAILY_API_KEY=...
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...
CARTESIA_API_KEY=...
```

### Run the script:
```
python voice_agent.py
```

Go to the Daily room and enjoy!



### Other useful links:

pipecat-ai docs: https://pipecat-ai.github.io/docs/intro
