import tomli


def tomli_load(file) -> dict:
    """正确处理 utf-16"""
    with open(file, "rb") as f:
        text = f.read()
        try:
            text = text.decode()  # Default encoding is 'utf-8'.
        except UnicodeDecodeError:
            text = text.decode("utf-16").encode().decode()
        return tomli.loads(text)
