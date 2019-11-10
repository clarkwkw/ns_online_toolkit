import telegram.error
import logging
from .errors import ProcessNotFoundException


class Bot:
    def __init__(
                    self,
                    tg_bot,
                    allowed_chats,
                    controller,
                    monitor,
    ):
        self.__tg_bot = tg_bot
        self.__allowed_chats = allowed_chats
        self.__controller = controller
        self.__monitor = monitor
        self.run_scheduler = True

    def send_screenshot(self, chat_id, screenshot, caption=None, retry=2):
        last_error = None
        for _ in range(retry+1):
            try:
                self.__tg_bot.send_photo(chat_id, screenshot.file, caption)
                last_error = None
                break
            except telegram.error.NetworkError as e:
                last_error = e
        if last_error is not None:
            raise last_error

    def send_message(self, chat_id, text,):
        self.__tg_bot.sendMessage(chat_id, text)

    def update_status(self, status):
        if status is not None:
            if status.on_locked_page:
                for id in self.__allowed_chats:
                    try:
                        self.send_screenshot(
                            id,
                            status.screenshot,
                            "Account locked, call the number"
                        )
                    except telegram.error.NetworkError:
                        self.send_message(
                            id,
                            "Account locked, call the number"
                        )
            elif not status.process_exists:
                self.send_message(
                    id,
                    "Process is dead, RIP"
                )

    def start_scheduler(self, update, context):
        self.run_scheduler = True
        self.send_message(id, "Started scheduler")

    def stop_scheduler(self, update, context):
        self.run_scheduler = False
        self.send_message(id, "Stopped scheduler")

    def request_screenshot_handler(self, update, context):
        try:
            if update.effective_chat.id not in self.__allowed_chats:
                return
            screenshot = self.__controller.take_screenshot()
            self.send_screenshot(update.effective_chat.id, screenshot)
        except telegram.error.NetworkError:
            logging.exception("Failed to send screenshot due to network error")
            self.send_message(
                update.effective_chat.id,
                "Failed to upload screenshot because of network error"
            )
        except ProcessNotFoundException:
            self.send_message(update.effective_chat.id, "Process is dead, RIP")
        except Exception as e:
            logging.exception("Failed to send screenshot due to unknown error")
            self.send_message(
                update.effective_chat.id,
                f"Failed to produce screenshot because of this error:\n{e}"
            )
