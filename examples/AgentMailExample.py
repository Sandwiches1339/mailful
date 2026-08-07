import mailful
import agentmail
import asyncio

client = mailful.MailfulClient(
    provider=mailful.get_provider_quick("agentmail"),
    
    api_key="xxxxxxxx",
    inbox_id="sandwichesarethebestmeow@agentmail.to", 
    verbose=True
)

async def main():
    await client.set_websocket(True)
    
    while True:
        continue

@client.on("MessageReceived")
async def receivemessage(data: mailful.MailMessage):
    print(data.html)
    
asyncio.run(
    main()
)