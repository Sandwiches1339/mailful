import mailful
import agentmail
import asyncio

client = mailful.MailfulClient(
    provider=mailful.get_provider_quick("agentmail"),
    
    api_key="am_us_6e3a9c773ad2380816fb536f490f10fb54783d4bac51797b69cfd65830c24b61",
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