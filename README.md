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
