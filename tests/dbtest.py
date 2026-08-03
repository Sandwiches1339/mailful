import mailful

from discord.embeds import Embed

abc = mailful.MailfulClient(mailful.get_provider_quick("smtp"),
    username="MS_4PpPc4@test-86org8ejmxkgew13.mlsender.net",
    password="mssp.egDDeOz.pxkjn41expqlz781.LALXYIP",
    host="smtp.mailersend.net",
    port="587",
    use_mozilla_certificate=True,
    verbose=True
)

newEmailful = mailful.EmailDraftful().add_subject("IMPORTANT!").add_html("<p>plz read</p>").add_text("plz read").add_to("kentanggorenghq@gmail.com")

abc.send_sync(newEmailful)