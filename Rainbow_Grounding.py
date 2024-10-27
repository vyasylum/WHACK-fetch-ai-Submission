import openai
from uagents import Agent, Context, Model
from gtts import gTTS
from pydub import AudioSegment
import os
import tempfile
from time import sleep

# Define the API key for OpenAI
openai.api_key = "sk-bdHfbYqiPR8QWOihKw34cKBahcJcERCRwMLU7-ZY3jT3BlbkFJn0W5FRj5B0PftxaGFLV9_mSiTxMASt80AGi4FKfjQA"


GROUNDING_ADDRESS_FILE = "grounding_address.txt"



class StressAlert(Model):
    message: str

class StressControl(Model):
    command: str

# Instantiate the Grounding Agent
grounding_agent = Agent(port=8000, endpoint=["http://localhost:8000/submit"])

# Function to fetch grounding exercise from OpenAI
async def get_grounding_exercise():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Give me a short, calming Rainbow Grounding exercise for someone driving, formatted as plain text with no headings or introductions. Make it simple and easy to follow, focusing on grounding through sight, hearing, and touch. Keep it concise."}
            ],
            max_tokens=350
        )
        grounding_text = response['choices'][0]['message']['content'].strip()
        print(f"[GroundingAgent]: Generated grounding exercise: {grounding_text}")
        return grounding_text
    except Exception as e:
        print(f"[GroundingAgent]: OpenAI API request failed: {e}")
        return "Take a deep breath and focus on your surroundings."

# Test function to check OpenAI API connectivity
def test_openai_connection():
    print("[GroundingAgent]: Testing OpenAI API connection...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Test successful'"}
            ],
            max_tokens=5
        )
        test_result = response['choices'][0]['message']['content'].strip()
        print(f"[GroundingAgent]: OpenAI API test successful, response: {test_result}")
    except Exception as e:
        print(f"[GroundingAgent]: OpenAI API test failed: {e}")

# Handle stress alerts
@grounding_agent.on_message(StressAlert)
async def grounding_exercise(ctx: Context, sender: str, alert: StressAlert):
    print(f"[GroundingAgent]: Received stress alert from {sender}. Initiating grounding exercise...")

    # Step 1: Notify StressAlert to pause detection
    pause_command = StressControl(command="pause")
    await ctx.send(sender, pause_command)
    print("[GroundingAgent]: Sent pause command to StressAlert agent.")

    # Step 2: Fetch grounding prompt using OpenAI API
    grounding_text = await get_grounding_exercise()

    # Step 3: Convert received text to audio using gTTS
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            tts = gTTS(grounding_text)
            tts.save(temp_audio_file.name)
            # Play audio externally using OS command
            os.startfile(temp_audio_file.name)  # Opens the audio file in the default player
            sleep(90)  # Delay to allow playback completion
    finally:
        # Ensure the temporary file is removed
        if os.path.exists(temp_audio_file.name):
            os.remove(temp_audio_file.name)
        print("[GroundingAgent]: Grounding audio playback completed.")

    # Step 5: Notify StressAlert agent to resume detection
    resume_command = StressControl(command="resume")
    await ctx.send(sender, resume_command)
    print("[GroundingAgent]: Sent resume command to StressAlert agent.")

if __name__ == "__main__":
    # Run the test function
    test_openai_connection()
    
    # Start the agent
    grounding_agent.run()
