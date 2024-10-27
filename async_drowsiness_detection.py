import cv2
import numpy as np
import asyncio
from tensorflow.keras.models import load_model
from playsound import playsound
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Fetch.ai mailbox and wallet setup
#AGENT_MAILBOX_KEY = ""   : mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai"
agent = Agent(name="Drowsy", seed="iejfvbklejfbv", port=8005,endpoint=["http://localhost:8005/submit"])

class Notify_Fleet_Manager(Model):
    message: str
RECIPIENT_ADDRESS_1 = "agent1qvydf9n3dqa7s3t5yf53cslcsxlvqkx9kgw3leng34uhdrtmxzk9vhnc52y"

# class Notify_Passenger(Model):
#     notifcation: str

# RECIPIENT_ADDRESS_2= "agent1q05s4tr4magu4f4lqdfz63mcevkkpw0h9sda65tmtjj9l8j6cy2wu6yqewg"
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
async def alarm_trigger(ctx): 
    try:
        ctx.logger.info("Alarm: Eyes detected as closed! Playing alarm sound...")
        playsound("alarm.wav")

        await ctx.send(RECIPIENT_ADDRESS_1, Notify_Fleet_Manager(message="Driver drowsiness detected! Alarm triggered."))
        ctx.logger.info(f"Alert message sent to {RECIPIENT_ADDRESS_1}")

        # await ctx.send(RECIPIENT_ADDRESS_2, Notify_Passenger(message="Driver drowsiness detected! Alarm triggered."))
        # ctx.logger.info(f"Alert message sent to {RECIPIENT_ADDRESS_2}")


    except Exception as e:
        print(f"Error playing alarm sound: {e}")

# alarm_count = 0

# Alarm trigger function to send alert and play sound
# async def alarm_trigger(ctx: Context):
#     global alarm_count
#     alarm_count += 1  

#     try:
#         ctx.logger.info("Alarm: Eyes detected as closed! Playing alarm sound...")
#         playsound("alarm.wav")

#         if alarm_count == 1:
#             # Send to passenger on the first alarm
#             await ctx.send(RECIPIENT_ADDRESS_2, Notify_Passenger(notifcation="Driver drowsiness detected! Alarm triggered."))
#             ctx.logger.info(f"Alert message sent to passenger at {RECIPIENT_ADDRESS_2}")
#         else:
#             # Send to fleet manager on subsequent alarms
#             await ctx.send(RECIPIENT_ADDRESS_1, Notify_Fleet_Manager(message="The driver is sleepy, please cancel further trips."))
#             ctx.logger.info(f"Alert message sent to fleet manager at {RECIPIENT_ADDRESS_1}")

#     except Exception as e:
#         print(f"Error playing alarm sound: {e}")

# Eye monitoring loop function
async def eye_monitoring_loop(ctx,model_path, interval=2):
    model = await load_model_async(model_path)
    video_capture = cv2.VideoCapture(0)  # First connected camera

    if not video_capture.isOpened():
        ctx.logger.info("Error: Could not open video stream.")
        return

    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                ctx.logger.info("Error: Failed to capture an image.")
                break

            # Assuming the frame is an image of the eyes (you may need to adjust this)
            status = await predict_eye_status_async(model, frame)
            ctx.logger.info("Eye status:", status)

            # Trigger alarm if eyes are closed
            if status == "closed":  
                await alarm_trigger(ctx)

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
    # Start eye monitoring as an async background task, passing ctx as well
    ctx.logger.info("Starting eye monitoring...")
    asyncio.create_task(eye_monitoring_loop(ctx, model_path, interval=2))

    

print("uAgent address: ", agent.address)

if __name__ == "__main__":
    agent.run()
