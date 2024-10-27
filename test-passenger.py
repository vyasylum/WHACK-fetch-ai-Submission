 
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model
 
class Notify_Passenger(Model):
    notifcation: str


sender = "agent1qt89kk828hyw63m8xyzr4tukj8meh3ulsjhhaxl3y3v49rujeqa978rpn7p"

Notify_Passenger = Agent(
    name="Notify_Passenger",
    port=5002,
    seed="jssdsndsjnvjsnslnmvklsmsklmvlksmldhdbfsjkhdbvdjkfhvb",
    endpoint=["http://localhost:5002/submit"]

)

fund_agent_if_low(Notify_Passenger.wallet.address())

@Notify_Passenger.on_message(model=Notify_Passenger)
async def message_handler(ctx: Context, sender: str, msg: Notify_Passenger):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")

 
if __name__ == "__main__":
    Notify_Passenger.run()
