import io


class Screenshot:
    def __init__(self, pil_img):
        self.pil_img = pil_img

    def __create_img_buffer(self):
        buffer = io.BytesIO()
        self.pil_img.save(buffer, format="PNG")
        return buffer

    @property
    def bytes(self):
        return self.__create_img_buffer().getvalue()

    @property
    def file(self):
        buffer = self.__create_img_buffer()
        buffer.seek(0)
        return io.BufferedReader(buffer)
