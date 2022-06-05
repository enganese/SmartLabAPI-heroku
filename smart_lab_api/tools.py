class Tools:
    def isfloat(num):
        """
        Check if a string is a float
        """

        try:
            float(num)
            return True
        except ValueError:
            return False

    def normalize_text(text: str) -> str | None:
        try:
            text = text.replace("\t", "").replace("\n", "").replace("\xa0", "")
            if len(text) == 1:
                return text.replace(" ", "Недоступно / Not available").replace("?", "")
            else:
                return text.replace(" ", "").replace("?", "")
        except:
            return None

    def normalize_text_2(text: str) -> str | None:
        try:
            text = str(text).replace("\t", "").replace("\n", " || ").replace("\xa0", "")
            return text
        except:
            return None
