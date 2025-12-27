# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from os import getenv

class Config:
    API_ID = int(getenv("30163640", 0))
    API_HASH = getenv("42f349f43dad2c998b0e50b0117c47fd")
    BOT_TOKEN = getenv("8546171122:AAFuB-MT27BDRjBDckyCPIZdhAy1Vi80CN4")

    # Force Subscribe Channel ID (Bot must be admin)
    CHID = int(getenv("CHID", 0))

    # Admin / Owner IDs
    SUDO = list(map(int, getenv("SUDO", "5678991839").split())) if getenv("SUDO") else []

    # MongoDB
    MONGO_URI = getenv("mongodb+srv://shaikharru99_db_user:k5llvkSQdf4ifAN7@cluster0.mo6eijj.mongodb.net/?appName=Cluster0")

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

# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01