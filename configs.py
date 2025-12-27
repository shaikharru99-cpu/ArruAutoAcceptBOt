# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01


from os import path, getenv

class Config:
    API_ID = int(getenv("API_ID", "30163640"))
    API_HASH = getenv("API_HASH", "42f349f43dad2c998b0e50b0117c47fd")
    BOT_TOKEN = getenv("BOT_TOKEN", "8546171122:AAFuB-MT27BDRjBDckyCPIZdhAy1Vi80CN4")
    # Your Force Subscribe Channel Id Below 
    CHID = int(getenv("CHID", "-1003440616450")) # Make Bot Admin In This Channel
    # Admin Or Owner Id Below
    SUDO = list(map(int, getenv("SUDO", "5678991839").split()))
    MONGO_URI = getenv("MONGO_URI", "mongodb+srv://shaikharru99_db_user:k5llvkSQdf4ifAN7@cluster0.mo6eijj.mongodb.net/?appName=Cluster0")
    
cfg = Config()

# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
