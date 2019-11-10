import json


class Status:
    def __init__(self, screenshot, process_exists, on_locked_page):
        self.screenshot = screenshot
        self.process_exists = process_exists
        self.on_locked_page = on_locked_page

    def __str__(self):
        return json.dumps({
                "process_exists": self.process_exists,
                "on_locked_page": self.on_locked_page
            },
            indent=4
        )
