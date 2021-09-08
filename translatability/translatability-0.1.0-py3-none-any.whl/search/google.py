from deep_translator import GoogleTranslator


def search(word):
    translator = GoogleTranslator(source="de", target="en")
    text = word

    try:
        translation = (
            translator.translate(text)
            if translator.translate(text) != text
            else False
        )
        return translation

    except ValueError:
        print(
            "You have exceeded the maximum number of queries with the "
            "GoogleTrans API. Consider activating a VPN. "
            "\n\nTranslations have been left empty."
        )
        empty = False
        return empty

    except ConnectionAbortedError:
        print(
            "Your connection has been interrupted. "
            "\n\nTranslations have been left empty."
        )
        empty = False
        return empty
