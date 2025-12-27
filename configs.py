from os import getenv

class Config:
    API_ID = int(getenv("API_ID", 0))
    API_HASH = getenv("API_HASH")
    BOT_TOKEN = getenv("BOT_TOKEN")

    # Force Subscribe Channel ID
    CHID = int(getenv("CHID", 0))

    # Admin IDs
    SUDO = list(map(int, getenv("SUDO", "").split())) if getenv("SUDO") else []

    # MongoDB
    MONGO_URI = getenv("MONGO_URI")

    @staticmethod
    def validate():
        if not all([
            Config.API_ID,
            Config.API_HASH,
            Config.BOT_TOKEN,
            Config.MONGO_URI
        ]):
            raise ValueError("❌ Missing required environment variables!")

cfg = Config()
cfg.validate()