_bot = None

def SetBot(bot):
    global _bot
    _bot = bot

def PassBot(func):
    def wrapper(*args, **kwargs):
        global _bot
        if _bot is None:
            raise Exception("Bot is not set")
        return func(*args, **kwargs, _bot=_bot)
    return wrapper  