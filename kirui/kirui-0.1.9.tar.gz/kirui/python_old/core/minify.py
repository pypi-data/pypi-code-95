

def minify(element):
    for child in element.childNodes:
        if child.nodeType == 3:
            text = child.textContent
            text = text.replace('\r\n', ' ')
            text = text.replace('\n', ' ')
            while '  ' in text:  # állítólag ez a leggyorsabb megoldás
                text = text.replace('  ', ' ')
            if text == ' ':
                element.removeChild(child)
                continue

            text = text.lstrip()
            child.textContent = text
        else:
            minify(child)
