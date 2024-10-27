import cv2
import numpy as np
import asyncio
from tensorflow.keras.models import load_model
from playsound import playsound
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

# Fetch.ai mailbox and wallet setup
AGENT_MAILBOX_KEY = "4acf2364-31be-4d59-984c-14975df61094"
agent = Agent(name="alice", seed="dkfhvbdhkfbv", mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai")

# Fund agent if wallet balance is low
fund_agent_if_low(agent.wallet.address())

# Asynchronous model loading
async def load_model_async(model_path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, load_model, model_path)

# Asynchronous eye status prediction function
async def predict_eye_status_async(model, eye_image):
    eye_image = cv2.resize(eye_image, (80, 80))
    eye_image = eye_image / 255.0
    eye_image = eye_image.reshape(1, 80, 80, 3)

    loop = asyncio.get_event_loop()
    prediction = await loop.run_in_executor(None, model.predict, eye_image)
    return "closed" if prediction[0][0] > 0.30 else "open"

# Alarm trigger to play sound
async def alarm_trigger():
    print("Alarm: Eyes detected as closed! Playing alarm sound...")
    playsound("alarm.wav")

# Eye monitoring loop function
async def eye_monitoring_loop(model_path, interval=2):
    model = await load_model_async(model_path)
    video_capture = cv2.VideoCapture(0)  # First connected camera

    if not video_capture.isOpened():
        print("Error: Could not open video stream.")
        return

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                print("Error: Failed to capture an image.")
                break

            # Assuming the frame is an image of the eyes (you may need to adjust this)
            status = await predict_eye_status_async(model, frame)
            print("Eye status:", status)

            # Trigger alarm if eyes are closed
            if status == "closed":
                await alarm_trigger()

            # Wait before the next check
            await asyncio.sleep(interval)

    finally:
        video_capture.release()
        cv2.destroyAllWindows()

# Trigger eye-monitoring loop when agent starts
@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")
    model_path = "model.h5"
    # Start eye monitoring as an async background task
    ctx.logger.info("Starting eye monitoring...")
    asyncio.create_task(eye_monitoring_loop(model_path, interval=2))

print("uAgent address: ", agent.address)

if __name__ == "__main__":
    agent.run()
