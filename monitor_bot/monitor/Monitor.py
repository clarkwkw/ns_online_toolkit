from .Status import Status
from ..errors import (
    ProcessNotFoundException
)
import schedule
import logging

LOCK_LABELS = ["3923-6625", "通訊安全鎖"]


class Monitor:
    def __init__(self, controller, vision_transport):
        self.controller = controller
        self.vision_transport = vision_transport

    def detect_status(self):
        try:
            sc = self.controller.take_screenshot()
            results = self.vision_transport.recognize_bytes(sc.bytes)

            return Status(
                screenshot=sc,
                process_exists=True,
                on_locked_page=self._on_locked_page(results)
            )
        except ProcessNotFoundException:
            logging.exception("Game process seems to be dead")
            return Status(
                screenshot=sc,
                process_exists=False,
                on_locked_page=False
            )
        except Exception:
            logging.exception("Failed to fetch status")
            return None

    def setup_regular_monitoring(self, interval, callbacks):
        schedule.every(interval).minutes.do(
            self.__monitor_and_trigger_callbacks,
            callbacks
        )

    def __monitor_and_trigger_callbacks(self, callbacks):
        logging.info("Performing regular check")
        status = self.detect_status()
        logging.info("Status %s" % str(status))
        for callback in callbacks:
            try:
                callback(status)
            except Exception:
                logging.exception(
                    "Failed to invoke callback after fetching status"
                )

    def _on_locked_page(self, recognition):
        for result in recognition:
            for label in LOCK_LABELS:
                if label in result.text:
                    return True
        return False
