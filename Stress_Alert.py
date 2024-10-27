import asyncio
from uagents.setup import fund_agent_if_low
from uagents import Context, Model, Agent
# Define the GroundingAgent address here
GROUNDING_AGENT_ADDRESS = "agent1qtwagy3lmkuxa6k2z9zmlylkc8zcf7nzkvxkqne8quywj809ew2a5yz9tz9"

# Message classes
class StressAlert(Model):
    message: str

class StressControl(Model):
    command: str

# Initialize the StressMonitor agent
stress_agent = Agent(
    name="StressMonitor",
    port=8008,
    seed="fake_seed_for_stress_monitor",
    endpoint=["http://localhost:8008/submit"]
)

# Fund the agent if balance is low
fund_agent_if_low(stress_agent.wallet.address())

# Monitoring function that checks for stress indicators
async def monitor_stress(ctx: Context):
    print("[StressMonitor]: Starting stress monitoring...")

    while True:
        # Simulate readings
        heart_rate = 112  # Placeholder for real data
        respiratory_rate = 15  # Placeholder for real data

        print(f"[StressMonitor]: Heart Rate: {heart_rate} bpm, Respiratory Rate: {respiratory_rate} breaths/min")

        # Stress condition
        if heart_rate > 100 or respiratory_rate > 20:
            print("[StressMonitor]: Stress detected! Triggering grounding support...")
            try:
                # Send alert to GroundingAgent
                await ctx.send(GROUNDING_AGENT_ADDRESS, StressAlert(message="Stress detected: Heart rate or respiratory rate high"))
                print("[StressMonitor]: Stress alert sent successfully to GroundingAgent")
            except Exception as e:
                print(f"[StressMonitor]: Failed to send stress alert: {e}")

        await asyncio.sleep(5)  # Adjust interval as needed for testing

# Startup event: Starts the monitoring task on startup
@stress_agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info("Stress Alert Agent started successfully.")
    # Start stress monitoring as a background task
    asyncio.create_task(monitor_stress(ctx))

# Event handler for handling stress detection
@stress_agent.on_event("stress_detected")
async def handle_stress(ctx: Context):
    alert = StressAlert(message="Stress detected! Initiating grounding support...")
    await ctx.send(GROUNDING_AGENT_ADDRESS, alert)
    ctx.logger.info("Sent stress alert to GroundingAgent")

    # Pause further stress detection
    pause_control = StressControl(command="pause")
    await ctx.send(GROUNDING_AGENT_ADDRESS, pause_control)
    ctx.logger.info("Sent pause command to GroundingAgent")

# Message handler for control messages
@stress_agent.on_message(StressControl)
async def handle_control(ctx: Context, sender: str, msg: StressControl):
    if msg.command == "resume":
        ctx.logger.info("Received resume command from GroundingAgent. Resuming stress detection.")

# Run the agent
if __name__ == "__main__":
    stress_agent.run()
