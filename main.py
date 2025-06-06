from keep_alive import keep_alive
from bot import bot
from auto_alerts import start_auto_loop

if __name__ == "__main__":
    keep_alive()
    start_auto_loop()
    print("🚀 FundingRadarBot is now online.")
    bot.infinity_polling()
