from monitor_bot.bot import Bot
from monitor_bot.controller import GameController
from monitor_bot.monitor import Monitor
from monitor_bot.transport import VisionTransport
from telegram.ext import Updater, CommandHandler
import argparse
import json
import logging
import schedule
import time
import threading


SHOULD_SHUT_DOWN = False


def maintain_scheduler(bot):
    logging.info("starting up scheduler")
    try:
        schedule.run_all()
        while not SHOULD_SHUT_DOWN:
            if bot.run_scheduler:
                schedule.run_pending()
            time.sleep(1)
    except Exception:
        import traceback
        traceback.print_exc()
    logging.info("shutting down scheduler")


def signal_handler(signum, frame):
    global SHOULD_SHUT_DOWN
    SHOULD_SHUT_DOWN = True


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--config",
    default="config.json",
    type=str
)
args = parser.parse_args()

logging.info("setting up bot")

config = None
with open(args.config, "r") as f:
    config = json.load(f)

controller = GameController()
monitor = Monitor(
    controller,
    VisionTransport(config["cloud_credentials_path"])
)
updater = Updater(
                token=config["tg_token"],
                use_context=True,
                user_sig_handler=signal_handler
)
bot = Bot(updater.bot, config["allowed_chats"], controller, monitor)
monitor.setup_regular_monitoring(
                config["monitor_interval"],
                [bot.update_status]
)
updater.dispatcher.add_handler(CommandHandler(
    "screenshot",
    bot.request_screenshot_handler
))
updater.dispatcher.add_handler(CommandHandler(
    "start_scheduler",
    bot.start_scheduler
))
updater.dispatcher.add_handler(CommandHandler(
    "stop_scheduler",
    bot.stop_scheduler
))

logging.info("starting polling")
threading.Thread(
                    target=maintain_scheduler,
                    name="maintain_scheduler",
                    args=[bot]
).start()
updater.start_polling(timeout=20)
updater.idle()
