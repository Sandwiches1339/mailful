import mailful

from discord.embeds import Embed

mailfulClient = mailful.MailfulClient(mailful.get_provider_quick("smtp"),
    username="xxxxxxxxxx",
    password="xxxxxxxxx",
    host="smtp.mailersend.net",
    port="587",
    use_mozilla_certificate=True,
    verbose=True
)

newEmailful = mailful.EmailDraftful()\
    .add_subject("IMPORTANT!")\
    .add_html("<p>plz read</p>")\
    .add_text("plz read")\
    .add_to("sandwichesarethebestmeow@gmail.com")

mailfulClient.send_sync(newEmailful)