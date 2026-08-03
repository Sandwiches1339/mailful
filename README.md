# 𑣲⋆📧 mailful 📧⋆❀
Unified, Modular, and Agnostic Asynchronous (but also Synchronous) mail client for multiple providers.

Not to be confused with Mailful, the service.

Picture yourself in this scenario:
You wanted to switch mail providers since your current provider is causing you problems. 
*But, oh no!* Without **mailful**, you would have to refactor a LOT of code just to switch from **AgentMail** to **SMTP**.
With **mailful**, you can leave all the messy code for a more simplistic approach on an email client.

# What is the current supported list of providers?
There is currently 2 supported, which is:
- AgentMail
- SMTP

Next release will add more. Stay tuned!

# Is this Asynchronous?
By default, yeah! But, if you want synchronous functions, just append _sync to the end of the current function.

I would love to see if it is better if mailful is mainly async or sync. Please tell me!

# If you say this is agnostic, and modular, can I just write my own Provider implementation?
Yeah! There is a BaseProvider (ABC) just for this scenario! I'll probably provide instructions on ways to make your own Provider, since the current way is very confusing.

# Can I switch providers without changing my code?
As said before, yeah. Though, I might've failed to convey it enough.

# Is this production-ready?
Well, mailful is still in... *active development*, so any bugs you find, please open an issue!
