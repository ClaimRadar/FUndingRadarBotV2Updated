from keep_alive import keep_alive
from bot import bot

if __name__ == "__main__":
    keep_alive()
    print("🚀 FundingRadarBot is now online.")
    bot.infinity_polling()
