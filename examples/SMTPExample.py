import mailful
import asyncio

mailfulClient = mailful.MailfulClient(mailful.get_provider_quick("smtp"),
    username="xxxxxxxxxx",
    password="xxxxxxxxx",
    host="smtp.mailersend.net",
    port="587",
    use_mozilla_certificate=True,
    verbose=True
)


mailTemplater = mailful.email_util.EmailClasses.EmailTemplate(
    """{{ start }}
    
    <p>You fails</p>
    
    {{ end }}"""
)

rendered_text = mailTemplater.render(
    
    start="<h1>My thing start</p>",
    end="<h1>My thing end</h1>"
    
)

newEmailful = mailful.EmailDraftful()\
    .add_subject("IMPORTANT!")\
    .add_html(rendered_text)\
    .add_text("plz read")\
    .add_to("sandwichesarethebestmeow@gmail.com")

mailfulClient.send_sync(newEmailful)