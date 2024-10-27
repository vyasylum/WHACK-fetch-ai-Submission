from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model


class Notify_Passenger(Model):
    notifcation: str

Notify_Passenger = Agent(
    name="Notify_Passenger",
    port=8001,
    seed="ksjhdfvkdftfjhbkjhnkldfhjbvhjdfb",
    endpoint=["http://localhost:8001/submit"]

)

fund_agent_if_low(Notify_Passenger.wallet.address())

@Notify_Passenger.on_message(model=Notify_Passenger)
async def message_handler(ctx: Context, sender: str, msg: Notify_Passenger):
    ctx.logger.info(f"Received message from {sender}: {msg.notifcation}")

 
if __name__ == "__main__":
    Notify_Passenger.run()

