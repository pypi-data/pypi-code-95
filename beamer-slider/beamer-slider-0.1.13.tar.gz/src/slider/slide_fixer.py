"""
Fix broken issues in osvg files.
for instance, you copy a random file, and it has the wrong dimensions, etc.
Need some fairly serious checking I guess...

Example of a good file:

inkscape:groupmode="layer"
     id="layer1"
     inkscape:label="bg_layer"
     style="display:inline"
     sodipodi:insensitive="true">
"""


good_file = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns:sodipodi = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
 xmlns:inkscape = "http://www.inkscape.org/namespaces/inkscape"
 height="297.638pt" version="1.2" viewBox="0 0 396.85 297.638" width="396.85pt" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><metadata></metadata>
<g inkscape:groupmode="layer" id="layer1" inkscape:label="bg_layer" style="display:inline" sodipodi:insensitive="true">
<image
xlink:href="{0}"
width="100%"
height="100%"
preserveAspectRatio="none"
style="image-rendering:optimizeQuality"
id="image4444th"
x="0"
y="0" />
</g>
<g inkscape:groupmode="layer"
id="layer2"
inkscape:label="Layer 1"
style="display:inline">
</svg>
"""

""""
First idea would be to simply load files, replace the tmp-stuff, and check if they agree.
"""
from bs4 import BeautifulSoup
import os

def check_svg_file_and_fix_if_broken(osvg_file, verbose=True):
    assert False
    '''
    Sanity check the given file. Does the slide appears to be in okay shape? Is it broken?
    if it is, fix it.
    '''
    # print(osvg_file)
    png_ = "tmp/" + os.path.basename(osvg_file)[:-4] + ".png"

    ID = 'image4444th'
    to_save = None
    with open(osvg_file, 'r', encoding="UTF-8",errors="surrogateescape") as f:
        soup = BeautifulSoup(f, 'xml', from_encoding="UTF-8")

        bg_tags = soup.findAll("image", {'id': ID})

        if len(bg_tags) == 0:
            print("uh oh. No background image found in", osvg_file)

        g = None
        is_file_ok = True
        for i in soup.findAll("g", {'inkscape:groupmode': 'layer'}):
            if i['inkscape:label'] == "bg_layer":
                g = i
        if g is not None:
            bgim = g.find("image")
            if bgim['id'] == ID:
                # We have a BG image, it has the right ID. Also check if the path matches.
                bg_png = bgim['xlink:href']

                if bg_png != png_:
                    print("Mismatching background PNGs", osvg_file)
                    print(bg_png, png_)
                    bgim['xlink:href'] = png_
                    to_save = soup.prettify(formatter="xml")

            else:
                print("We found the bg_layer tag, but it has no image in it. SVG is broken", osvg_file)
                is_file_ok = False
        else:
            is_file_ok = False

        if is_file_ok:
            # Do sanity check of svg height property.
            height = soup.find('svg')['height']
            if height.find("pt") > 0:
                height = height[:-2]
            height = float(height)
            # float(soup.find('svg')['height'])
            if abs(height - 297.638) > 5:
                is_file_ok = False

    if to_save is not None:
        # raise Exception("asdfsdaf", osvg_file)
        with open(osvg_file, 'w', encoding="UTF-8", errors="surrogateescape") as f:
            f.write(to_save)
        return

    if not is_file_ok:
        # raise Exception("Broken file", osvg_file)
        # File is not ok. We have to fix it. But how?

        gsoup = BeautifulSoup(good_file, 'xml', from_encoding="UTF-8")
        bstag = BeautifulSoup(str(gsoup.svg.g).format(png_), 'lxml', from_encoding="UTF-8")
        g_bg = str(bstag.g)
        with open(osvg_file, 'r', encoding="UTF-8", errors="surrogateescape") as f:
            s = f.read()
            soup = BeautifulSoup(s, 'xml', from_encoding="UTF-8")
            print("Finding all tags")

            for j in soup.svg.find_all(recursive=False):
                IL= "inkscape:label"
                if IL in j.attrs and j[IL] == "bg_layer":
                    # gsoup = BeautifulSoup(good_file, 'xml', from_encoding="UTF-8")
                    j.replaceWith(bstag.g)
                    # print( j['inkscape:label']  )
                    break
                    # print("FOUND")
                # print(j)
                # c += 1
                # print(c, "-----")
                # if c == 4:
                #     break

            soup.svg.attrs = gsoup.svg.attrs
            s = str(soup)
            # j = s.find("<defs")
            # print("Found defs at j", j)
            # s = good_file.format( png_) + "\n" + s[j:]
        # import time
        # time.sleep(0.1)
        # print(s[:4000])
        # soup2 = BeautifulSoup(s, 'xml', from_encoding="UTF-8")

        with open(osvg_file, 'w', encoding="UTF-8", errors="surrogateescape") as f:
            f.write(s)
    a = 234