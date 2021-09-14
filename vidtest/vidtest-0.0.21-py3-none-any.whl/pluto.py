# Pluto
# v0.1.0

import numpy as np
import matplotlib.pyplot as plt
import cv2

import time
import webbrowser

def read_image(path: str, no_BGR_correction=False):  # -> np.ndarray
    """Returns an image from a path as a numpy array
    
    Args:
        path: location of the image.
        no_BGR_correction: When True, the color space is not converted from BGR to RGB
    
    Returns:
        The read image as np.ndarray.
    
    Raises:
        AttributeError: if path is not valid, this causes image to be None
    """
    image = cv2.imread(path)
    if image is None: raise AttributeError("Pluto ERROR in read_image() function: Image path is not valid, read object is of type None!")
    if no_BGR_correction: return image
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def show_image(image: np.ndarray, BGR2RGB=False):
    """Displays an image using matplotlib's pyplot.imshow()
    
    Args:
        image: The image to be displayed.
        BGR2RGB: When True, the color space is converted from BGR to RGB.
    """
    if BGR2RGB: image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.show()

def avg_of_row(img: np.ndarray, row: int, ovo=False):  # -> int | list
    """Calculates the average pixel value for one row of an image
    
    Args:
        img: The screenshot as np.ndarray
        row: which row of the image should be analysed?
        ovo: output as 'one value only' instead of list?
    
    Returns:
        The average value per row, ether one value only or per color channel value
    """
    all_values_added = 0
    if img.shape[2] == 3: all_values_added = [0, 0, 0]
    length = len(img)
    for pixl in img[row]: all_values_added += pixl
    out = all_values_added / length
    if ovo: out = sum(out) / 3
    return out

def avg_of_collum(img: np.ndarray, collum: int, ovo=False):  # -> int | list
    """Calculates the average pixel value for one collum of an image
    
    Args:
        img: The screenshot as np.ndarray
        collum: which collum of the image should be analysed?
        ovo: output as 'one value only' instead of list?
    
    Returns:
        The average value per collum, ether one value only or per color channel value
    """
    all_values_added = 0
    if img.shape[2] == 3: all_values_added = [0, 0, 0]
    length = len(img[0])
    for pixl in img[:, collum]: all_values_added += pixl
    out = all_values_added / length
    if ovo: out = sum(out) / 3
    return out

def trimm_and_blur(inpt: np.ndarray, less: bool, value: int, blurs, trimm, double_down=False, invert=None):
    for i in range(len(inpt)):
        for j in range(len(inpt[i])):
            if less:
                if inpt[i][j][0] > value or inpt[i][j][1] > value or inpt[i][j][2] > value:
                    inpt[i][j] = np.array(trimm)
                elif double_down:
                    inpt[i][j] = np.array(invert)
            else:
                if inpt[i][j][0] < value or inpt[i][j][1] < value or inpt[i][j][2] < value:
                    inpt[i][j] = np.array(trimm)
                elif double_down:
                    inpt[i][j] = np.array(invert)
    blur = cv2.blur(inpt, blurs)
    return blur

def to_grayscale(img: np.ndarray): # -> np.ndarray
    """Converts a color image to grayscale.
    Note: If the input image has dimensions of 200x200x3, the output image will have dimensions of 200x200.
    
    Args:
        img: color image with BGR channel order
    
    Returns:
        The input image as grayscale.
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def iso_grayscale(img: np.ndarray, less_than, value, convert_grayscale=False, blur=(1, 1)): # -> np.ndarray
    """Isolates image areas with a specific value
    
    Args:
        img: input image as np.ndarray
        less_than: Sets filter technique to less than / bigger than
        value: Value to filter by
        convert_to:grayscale: True if the input image is color and needs to be converted to grayscale first
        blur: optional blur kernal size
    
    Returns:
        modified input image as np.ndarray
    """
    if convert_grayscale: img = to_grayscale(img)

    if less_than:
        for i in range(len(img)):
            for j in range(len(img[i])):
                if img[i][j] < value: img[i][j] = 255
                else: img[i][j] = 0
    else:
        for i in range(len(img)):
            for j in range(len(img[i])):
                if img[i][j] > value: img[i][j] = 255
                else: img[i][j] = 0
    
    if blur != (1, 1):
        img = cv2.blur(img, blur)
    
    return img

def expand_to_rows(image: np.ndarray, full=False, value=200):  # -> np.ndarray
        """
        Args:
            image: An grayscale image as np.ndarray, which represents a mask.
        
        Returns:
            A np.ndarray of the edited image.
        """
        dimensions = image.shape
        imglen = dimensions[0]
        
        white_row = np.array([255 for k in range(dimensions[1])])
        black_row = np.array([0 for k in range(dimensions[1])])
        
        if not full: imglen = dimensions[0] / 2
        for i in range(int(imglen)):
            for j in range(dimensions[1]):
                if image[i][j] > value:
                    image[i] = white_row
        for i in range(int(imglen), dimensions[0]):
            for j in range(dimensions[1]):
                image[i] = black_row
        return image

def expand_to_columns(image: np.ndarray, full=False, value=200):  # -> np.ndarray
        """
        Args:
            image: An grayscale image as np.ndarray, which represents a mask.
        
        Returns:
            A np.ndarray of the edited image.
        """
        dimensions = image.shape
        imglen = dimensions[1]
        if not full: imglen = dimensions[1] / 2
        for i in range(int(imglen)):
            for j in range(dimensions[0]):
                if image[j][i] > value:
                    image[:,i] = [255 for k in range(dimensions[1])]
        for i in range(int(imglen), dimensions[1]):
            for j in range(dimensions[1]):
                image[j][i] = 0
        return image

class PlutoObject:
    def __init__(self, img: np.ndarray):
        self.img = img
        self.tesseract_path = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    
    def ocr(self, image=None):  # -> str
        """Preforms OCR on a given image, using ether Tesseract or EasyOCR
        
        Args:
            image: np.ndarray of the to be treated image.
        
        Returns:
            String with the raw result of the OCR library.
        
        """
        if image is None: image = self.img
        if self.tesseract_path == "": print("Pluto WARNING - Please check if tesseract_path has been set.")
        from pytesseract import pytesseract
        try:
            pytesseract.tesseract_cmd = self.tesseract_path
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print("Pluto WARNING - Error while performing OCR: ", e)
            text = ""
        return text

        print("Pluto WARNING - Check if use_tesseract and use_easyocr attributes are set.")
        return None

    def expand_to_rows(self, image: np.ndarray, full=False, value=200):  # -> np.ndarray
        """
        Args:
            image: An grayscale image as np.ndarray, which represents a mask.
        
        Returns:
            A np.ndarray of the edited image.
        """
        dimensions = image.shape
        imglen = dimensions[0]
        if not full: imglen = dimensions[0] / 2
        for i in range(int(imglen)):
            for j in range(dimensions[1]):
                if image[i][j] > value:
                    image[i] = [255 for k in range(dimensions[1])]
        for i in range(int(imglen), dimensions[0]):
            for j in range(dimensions[1]):
                image[i][j] = 0
        return image
    
    def ocr_cleanup(self, text: str):  # -> str
        """Removes unwanted characters or symbols from a text
        
        This includes \n, \x0c, and multiple ' ' 
        
        Args:
            text: The String for cleanup.
        
        Returns:
            The cleaned text as String.
        """
        out = text.replace("\n", " ")
        out = out.replace("\x0c", "")
        out = " ".join(out.split())
        
        splits = out.split(",")
        clean_splits = []
        
        for phrase in splits:
            arr = list(phrase)
            l = len(arr)
            start = 0
            end = l
            for i in range(0, l):
                if arr[i] == " ": start += 1
                else: break
            for i in range(l, 0, -1):
                if arr[i-1] == " ": end -= 1
                else: break
            clean_splits.append(phrase[start:end])
        
        out = ""
        for phrase in clean_splits:
            out += phrase
            out += ", "
        out = out[:-2]
        
        return out

    def to_json(self, data: dict):
        import json
        out = json.dumps(data)
        return out

    def extr_mask_img(self, mask: np.ndarray, img: np.ndarray, inverted=False):
        """Performs extend_to_rows() on the mask and returns the masked out parts of the original image.
        
        Args:
            mask: grayscale mask
            img: Original image
            inverted: if True, an inverted version of the output will also be returned
        
        Returns:
            A np.ndarray of the masked out part
        """
        mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
        
        extr = self.expand_to_rows(mask)
        
        # show_image(extr)
        
        out = []
        invout = []
        for i in range(len(extr)):
            if extr[i][0] > 200: out.append(img[i])
            elif inverted: invout.append(img[i])
        
        if inverted: return np.array(out), np.array(invout)
        return np.array(out)

class Twitter(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def dark_mode(self, img=None):  # -> bool
        """Checks if the screenshot has dark mode enabled
        
        Args:
            img: if the checked image should be different from the self.img, pass it here
        
        Returns:
            Is the screenshot in dark mode? True / False
        """
        testimg = self.img
        if img is not None: testimg = img.copy()
        top_row = avg_of_row(testimg, 0, True)
        bottom_row = avg_of_row(testimg, -1, True)
        left_collum = avg_of_collum(testimg, 0, True)
        right_collum = avg_of_collum(testimg, -1, True)
        final_value = sum([top_row, bottom_row, left_collum, right_collum]) / 4
        return final_value < 125
    
    def analyse(self):
        result = None
        if self.dark_mode(): result = self.dark()
        else: result = self.std()
        header, body = result
        # show_image(header)
        # show_image(body)
        return self.ocr_cleanup(self.ocr(header)), self.ocr_cleanup(self.ocr(body))
    
    def std(self, img=None, display=False):
        input_img = None
        if img is not None: input_img = img.copy()
        else: input_img = self.img.copy()
        if img is not None: self.img = img.copy()
        
        blur = trimm_and_blur(input_img, True, 30, (20, 20), [255, 255, 255])
        out = trimm_and_blur(blur, False, 250, (5, 5), [0, 0, 0])

        msk_inv = (255 - out[:,:,0])

        out_exptr = self.expand_to_rows(msk_inv, True)

        header_info = []
        continue_please = True
        cnt = 0
        for i in range(len(out_exptr)):
            if continue_please:
                if out_exptr[i][0] < 250: continue
            else:
                if out_exptr[i][0] < 250: break
            header_info.append(self.img[i])
            continue_please = False
            # print("hey!")
        cnt = i

        bottom = []
        lastone = False
        for i in range(cnt+1, len(out_exptr), 1):
            if out_exptr[i][0] < 250:
                if lastone:
                    bottom.append(self.img[3])
                    lastone = False
                continue
            bottom.append(self.img[i])
            lastone = True
        
        header_info = np.array(header_info)
        bottom = np.array(bottom)
        
        if display:
            show_image(header_info)
            show_image(bottom)
        
        return header_info, bottom
    
    def dark(self, img=None, display=False):
        """Segmentates the input screenshot (dark mode enabled) into header and body.
        
        Args:
            img: if the screenshot should be different from self.img, pass it here.
            display: True if output should be displayed before return
        
        Returns:
            The two segmentated areas.
        """
        input_img = None
        if img is not None: input_img = img.copy()
        else: input_img = self.img.copy()
        if img is not None: self.img = img.copy()
        
        blur = trimm_and_blur(input_img, False, 230, (20, 20),[0, 0, 0])
        out = trimm_and_blur(blur, True, 10, (5, 5),[255, 255, 255])

        msk = out[:,:,0]

        out_exptr = self.expand_to_rows(msk, True)

        header_info = []
        continue_please = True
        cnt = 0
        for i in range(len(out_exptr)):
            if continue_please < 3:
                if out_exptr[i][0] < 250:
                    if continue_please == 1: continue_please += 1
                    if continue_please == 2: header_info.append(self.img[i])
                    continue
            else:
                if out_exptr[i][0] < 250: break
            
            if continue_please == 0: continue_please += 1
            if continue_please == 2: break
            header_info.append(self.img[i])
        cnt = i

        bottom = []
        lastone = False
        for i in range(cnt+1, len(out_exptr), 1):
            if out_exptr[i][0] < 250:
                if lastone:
                    bottom.append(self.img[3])
                    lastone = False
                continue
            bottom.append(self.img[i])
            lastone = True
        
        header_info = np.array(header_info)
        bottom = np.array(bottom)
        
        if display:
            show_image(header_info)
            show_image(bottom)
        
        return header_info, bottom
    
    def black(self):
        pass

class FoxNews(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def analyse(self, display=False):
        og_shape = self.img.shape
        img = cv2.resize(self.img, (512, 512))
        black = np.zeros((512, 512))

        for i in range(len(black)):
            for j in range(len(black[0])):
                temp = img[i][j]
                if (temp == [34, 34, 34]).all(): black[i][j] = 255
        blured = cv2.blur(black, (20, 20))

        for i in range(len(blured)):
            for j in range(len(blured[0])):
                if blured[i][j] < 40: blured[i][j] = 0
                else: blured[i][j] = 255

        msk = self.expand_to_rows(blured)

        og_size_msk = cv2.resize(msk, (og_shape[1], og_shape[0]))
        
        top = []
        heading = []
        bottom = []

        top_part = True
        bottom_part = False

        for i in range(len(self.img)):
            if og_size_msk[i][0] > 1:
                heading.append(self.img[i])
                if top_part:
                    top_part = False
                    bottom_part = True
            elif top_part: top.append(self.img[i])
            else: bottom.append(self.img[i])

        heading = np.array(heading)
        bottom = np.array(bottom)
        top = np.array(top)
        
        if display:
            show_image(heading)
            show_image(bottom)
            show_image(top)

        ocr_result = self.ocr(heading)
        headline = self.ocr_cleanup(ocr_result)

        cat_info_img = []
        top_len = len(top)
        for i in range(top_len, 0, -1):
            if top[i-1][0][0] > 250: cat_info_img.insert(0, top[i-1])
            else: break

        cat_info_img = np.array(cat_info_img)
        print(cat_info_img.shape)
        if display: show_image(cat_info_img)

        ocr_result = self.ocr(cat_info_img)
        clean_ocr = self.ocr_cleanup(ocr_result)

        dotsplit = clean_ocr.split("-")[0][:-1].lstrip(" ")
        pubsplit = clean_ocr.split("Published")[1].lstrip(" ")
        
        subinfo_bottom = []

        stoper = False
        for row in bottom:
            subinfo_bottom.append(row)
            for pix in row:
                if pix[0] > 200 and pix[0] < 240 and pix[2] < 50 and pix[1] < 50:
                    stoper = True
                    break
            if stoper: break

        subinfo_bottom = np.array(subinfo_bottom[:-3])
        if display: show_image(subinfo_bottom)
        subinfo = self.ocr_cleanup(self.ocr(subinfo_bottom))

        subsplit = subinfo.split()

        author_list = []
        subtitle_list = []
        subinfo_switcher = True

        for w in reversed(subsplit):
            if w == "By" and subinfo_switcher:
                subinfo_switcher = False
                continue
            if w == "News" or w == "Fox" or w == "|": continue
            if subinfo_switcher: author_list.insert(0, w)
            else: subtitle_list.insert(0, w)

        author = " ".join(author_list)
        subtitle = " ".join(subtitle_list)
        
        jasoon = {  "source": "News Article",
                    "article": {
                        "created": "[Published] " + pubsplit,
                        "organisation": "Fox News",
                        "headline": headline,
                        "subtitle": subtitle,
                        "author": author,
                        "category": dotsplit
                    }
                }
        
        return self.to_json(jasoon)

class Facebook(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
        self.top = None
        self.body = None
        self.engagement = None
    
    def analyse(self, img=None, display=False): # -> tuple [str, str, str, str]
        """Main method for extracting information from a screenshot of a Facebook post.
        
        Args:
            img: If the used screenshot should differ from self.img, pass it here
            display: True for showing in-between steps
        
        Returns:
            The extracted information as a tuple of Strings
        """
        if img is None: img = self.img
        
        self.split(img)
        
        # t1 = time.time()
        top = to_grayscale(self.top)

        topname = top[:52,:]
        topdate = top[52:,:]
        
        if display:
            show_image(topname)
            show_image(topdate)
            show_image(self.middle)
        # t2 = time.time()
        # print("top name, date:", t2 - t1)
        # print(self.ocr(topname, True))
        # print(self.ocr(topdate, True))
        # show_image(self.middle)
        # show_image(self.bottom)
        # print(self.ocr(self.middle, True))
        # print("-------")
        # t1 = time.time()
        name = self.ocr_cleanup(self.ocr(topname))
        date = self.ocr_cleanup(self.ocr(topdate))
        
        body_text = self.ocr_cleanup(self.ocr(self.body))
        engagement_text = self.ocr_cleanup(self.ocr(self.engagement))
        # t2 = time.time()
        # print("ocr time:", t2 - t1)
        # bottomsting = self.ocr_cleanup(self.ocr(bottom))

        # print(name, date)
        # print(bottomsting)

        # print(self.characters_filter_strict(name, False), "|", self.characters_filter_strict(date))
        # print(self.characters_filter_strict(bottomsting))
        
        return name, date, body_text, engagement_text
    
    def dark_mode(self, img=None):
        if img is None: img = self.img
        dim = img.shape
        img = img[:int(dim[0]*0.1),:int(dim[0]*0.02),:]
        avg = np.average(img)
        return avg < 240

    def split(self, img=None, darkmode=None): # -> np.ndarray
        """Splits a Facebook Screenshot into a top part (thst's where the header is) and a 'bottom' part.
        
        Args:
            img: Alternative to the default self.img
        
        Returns:
            The top part and the bottom part, both as np.ndarray
        """
        if img is None: img = self.img
        og = img.copy()
        
        if darkmode is None: darkmode = self.dark_mode(img)
        # print(darkmode)
        
        if darkmode: gry = iso_grayscale(img, False, 50, True)
        else: gry = iso_grayscale(img, True, 250, True)

        gry_extr = expand_to_rows(gry, False, 100)
        
        top = []
        middle = []

        c = 0
        for i in range(len(gry_extr)):
            if gry_extr[i][0] > 100 and c < 2:
                if c == 0: c += 1
                top.append(og[i])
            elif c == 1: c += 1
            elif c == 2: middle.append(og[i])
        
        top = np.array(top)
        middle = np.array(middle)
        
        non_color = []
        for i in range(len(middle)):
            pix = middle[i][5] 
            if pix[0] > 250 or pix[1] > 250 or pix[2] > 250:
                non_color.append(middle[i])

        non_color = np.array(non_color)

        rgh = to_grayscale(non_color)

        rgh = rgh[:, int(non_color.shape[1] / 2):]
        rgh = iso_grayscale(rgh, True, 10, False, (25, 25))
        rgh = expand_to_rows(rgh, True, 5)
        
        body = []
        engagement = []
        for i in range(len(rgh)):
            if rgh[i][0] > 200: body.append(non_color[i])
            else: engagement.append(non_color[i])

        body = np.array(body)
        engagement = np.array(engagement)
        
        self.top = top
        self.body = body
        self.engagement = engagement
        
        return top, body, engagement

class NYT(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
        self.header_img = None
    
    def header(self, img=None, non_header=False):
        """Isolates the headline from an article, based on color
        
        Args:
            img: if the used screenshot should differ from self.img, pass it here
            non_header: True if all other parts of the screenshot, that don't belong to the headline, \
                        should also be returned seperatly (basicly a inverted return of this method)
        
        Returns:
            An isolated part of the original screenshot, which only contains the headline\
            (optional also an inverted version, when non_header is True)
        """
        if img is None: img = self.img.copy()
        img_og = img.copy()
        
        img = cv2.resize(img, (255, 255))
        img = trimm_and_blur(img, False, 30, (15, 15), [255, 255, 255], True, [0, 0, 0])
        
        extr = expand_to_rows(img[:,:,0], True, 10)
        extr = cv2.resize(extr[:,:10], (10, img_og.shape[0]))
        
        out = []
        inverse_out = []
        
        for i in range(len(extr)):
            if extr[i][0] > 200: out.append(img_og[i])
            elif non_header: inverse_out.append(img_og[i])
        
        out = np.array(out)
        
        if non_header: return out, inverse_out
        return out

    def images(self, img=None, non_images=False): # -> np.ndarary | None
        """Isolates images of an article, based on color
        
        Args:
            img: if the used screenshot should differ from self.img, pass it here
            non_images: True if all other parts of the screenshot, that aren't partof an image, \
                        should also be returned seperatly (basicly a inverted return of this method)
        
        Returns:
            An isolated part of the original screenshot, which only contains the headline\
            (optional an inverted version as well, when non_images is True)
            If no images can be found, the return is None
        
        Please make sure that img is not scaled down and *not* grayscale
        """
        if img is None: img = self.img.copy()
        
        img_og = img.copy()
        img = cv2.resize(img, (50, img_og.shape[0]))
        
        image = []
        non_image = []
        
        j = 0
        stop = False
        
        for i in range(len(img)):
            stop = False
            while j < len(img[i]) and not stop:
                pix = img[i][j]
                minpix, maxpix = np.min(pix), np.max(pix)
                difference = maxpix - minpix
                if difference > 0:
                    image.append(img_og[i])
                    stop = True
                
                j += 1
            
            if not stop and non_images: non_image.append(img_og[i])
            j = 0
        
        image = np.array(image)
        if non_images: non_image = np.array(non_image)

        if len(image) < 1:
            image = None
            print("Pluto WARNING - At least one return from images() is empty.")
        
        if non_images: return image, non_image
        return image
    
    def suber(self, img=None):
        """Isolates the headline from an article, based on color
        
        Args:
            img: if the used screenshot should differ from self.img, pass it here
            non_header: True if all other parts of the screenshot, that don't belong to the headline, \
                        should also be returned seperatly (basicly a inverted return of this method)
        
        Returns:
            An isolated part of the original screenshot, which only contains the headline\
            (optional also an inverted version, when non_header is True)
        """
        if img is None: img = self.img.copy()
        img_og = img.copy()
        
        img = cv2.resize(img, (255, 255))
        img = trimm_and_blur(img, False, 55, (15, 15), [255, 255, 255], True, [0, 0, 0])
        
        extr = expand_to_rows(img[:,:,0], True, 10)
        extr = cv2.resize(extr[:,:10], (10, img_og.shape[0]))
        # show_image(extr)
        out = []
        
        for i in range(len(extr)):
            if extr[i][0] > 200: out.append(img_og[i])
        
        out = np.array(out)
        return out
    
    def analyse(self, img=None):
        analyse_img = img
        if analyse_img is None: analyse_img = self.img
        color_images, non_color = self.images(analyse_img, True)
        
        head, body = self.header(non_color, True)
        # return head, body
        
        headline = self.ocr_cleanup(self.ocr(head))
        # print(headline)
        
        # show_image(head)
        # show_image(body)
        
        # print(type(body))
        subt = self.suber(np.array(body))
        subtitle = self.ocr_cleanup(self.ocr(subt))
        
        return headline, subtitle
    
    def to_json(self, img=None, path=None):
        if img is None: img = self.img.copy()
        import json
        result = self.analyse(img)
        
        jasoon = {  "source": "News Article",
                    "article": {
                        "organisation": "New York Times",
                        "headline": result[0],
                        "subtitle": result[1],
                    }
                }
        
        if path == None: return json.dumps(jasoon)
        else:
            out = open(path, "w")
            json.dump(jasoon, out, indent=6)
            out.close()
    
    def search(self, query: str):
        """Searches a query with the NYT's search function. Opens result in browser window.
        """
        link = "https://www.nytimes.com/search?query="
        query.replace(" ", "+")
        
        webbrowser.open((link + query))

class Tagesschau(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def analyse(self, img=None):
        if img is None: img = self.img
        
        head, no_head = self.header(img)
        
        # show_image(head)
        # show_image(no_head)
        
        info, body = self.info_split(no_head)
        
        head_ocr_result = self.ocr_cleanup(self.ocr(head))
        info_ocr_result = self.ocr_cleanup(self.ocr(info))
        body_ocr_result = self.ocr_cleanup(self.ocr(body))
        
        info_ocr_split = info_ocr_result.split("Stand:")
        if info_ocr_split[1][0] == " ": info_ocr_split[1] = info_ocr_split[1][1:]
        
        # print(head_ocr_result)
        # print(info_ocr_split[0])
        # print(info_ocr_split[1])
        # print(body_ocr_result)
        
        jasoon = {  "source": "News Article",
                    "article": {
                        "created": "[Published] " + info_ocr_split[0],
                        "organisation": "Fox News",
                        "headline": head_ocr_result,
                        "body": body_ocr_result,
                        "category": info_ocr_split[1]
                    }
                }
        
        return self.to_json(jasoon)
    
    def header(self, img=None):
        if img is None: img = self.img
        
        dim = img.shape
        
        to_grayscale(img)
        
        no_header = iso_grayscale(img, True, 90, True, (15, 15))
        no_header_exptr = expand_to_rows(no_header[:,:int(no_header.shape[1] / 4)], True, 5)
        
        head = []
        no_head = []
        
        for i in range(len(img)):
            if no_header_exptr[i][0] > 100: no_head.append(img[i])
            else: head.append(img[i])
        
        head = np.array(head)
        no_head = np.array(no_head)
        
        return head, no_head
    
    def info_split(self, img=None):
        if img is None: img = self.img
        
        # img_og = img.copy()
        
        iso = trimm_and_blur(img[:,:int(img.shape[1] / 4),:].copy(), False, 70, (10, 10), [255, 255, 255], True, [0, 0, 0])
        iso = expand_to_rows(iso[:,:,0], False, 5)
        # show_image(iso)
        
        info = []
        body = None
        
        for i in range(len(img)):
            if iso[i][0] < 100: info.append(img[i])
            else:
                body = img[i:,:,:]
                break
        
        info = np.array(info)
        # show_image(info)
        # show_image(body)
        
        return info, body

class WPost(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def analyse(self, img=None):
        if img is None: img = self.img
        
        category, headline, img_bottom = self.category()
        
        author, body = self.author(img_bottom)
        
        date, body = self.date(body)
        
        return category, headline, author, date, body
    
    def category(self, img=None, do_ocr=True, display=False):
        if img is None: img = self.img
        
        if display: show_image(img)
        color, img_top, img_bottom = self.images(img, True)
        if display:
            show_image(color)
            show_image(img_top)
            show_image(img_bottom)
        
        iso_top = iso_grayscale(img_top.copy(), False, 230, True, (10, 10))
        iso_expt = expand_to_rows(iso_top[:, :int(iso_top.shape[1] / 3)], True, 3)
        
        category = []
        headline = []
        for i in range(len(iso_expt)):
            if iso_expt[i][0] > 100: category.append(img_top[i])
            else: headline.append(img[i])
        
        category = np.array(category)
        headline = np.array(headline)
        
        if do_ocr: return self.ocr_cleanup(self.ocr(category)), \
                        self.ocr_cleanup(self.ocr(headline)), img_bottom
        return category, headline, img_bottom
    
    def author(self, img=None, do_ocr=True, display=False):
        if img is None: img = self.img
        
        iso = iso_grayscale(img, False, 235, True, (10, 10))
        iso = expand_to_rows(iso, True, 10)
        
        body_start = False
        
        out = []
        body = []
        for i in range(len(img)):
            if iso[i][0] > 100:
                out.append(img[i])
                body_start = True
            elif body_start: body.append(img[i])
        
        out = np.array(out)
        body = np.array(body)
        
        if display:
            show_image(out)
            show_image(body)
        
        if do_ocr:
            ocr_result = self.ocr_cleanup(self.ocr(out))
            ocr_result = ocr_result[3:].replace(" and", ",")
            return ocr_result, body

        return out, body
    
    def date(self, img=None, do_ocr=True, display=False):
        if img is None: img = self.img
        
        iso = iso_grayscale(img, False, 215, True, (10, 10))
        iso = expand_to_rows(iso, True, 10)
        
        body = []
        date = []
        
        for i in range(len(img)):
            if iso[i][0] > 100: body.append(img[i])
            else: date.append(img[i])
        
        out = np.array(date)
        body = np.array(body)
        
        if display:
            show_image(out)
            show_image(body)
        
        if do_ocr: return self.ocr_cleanup(self.ocr(out)), self.ocr_cleanup(self.ocr(body))
        return out, body
    
    def images(self, img=None, non_images=False): # -> np.ndarary | None
        """Isolates images of an article, based on color (WPost version)
        
        Args:
            img: if the used screenshot should differ from self.img, pass it here
            non_images: True if all other parts of the screenshot, that aren't partof an image, \
                        should also be returned seperatly (basicly a inverted return of this method)
        
        Returns:
            An isolated part of the original screenshot, which only contains the headline\
            (optional an inverted version as well, when non_images is True)
            If no images can be found, the return is None
        
        Please make sure that img is not scaled down and *not* grayscale
        """
        if img is None: img = self.img.copy()
        
        img_og = img.copy()
        img = cv2.resize(img, (50, img_og.shape[0]))
        
        image = []
        non_image_top = []
        non_image_bottom = []
        
        j = 0
        stop = False
        color_start = False
        
        for i in range(len(img)):
            stop = False
            while j < len(img[i]) and not stop:
                pix = img[i][j]
                minpix, maxpix = np.min(pix), np.max(pix)
                difference = maxpix - minpix
                if difference > 0:
                    image.append(img_og[i])
                    stop = True
                
                j += 1
            
            if stop: color_start = True
            
            if not stop and non_images:
                if color_start: non_image_bottom.append(img_og[i])
                else: non_image_top.append(img_og[i])
            j = 0
        
        image = np.array(image)
        if non_images:
            non_image_top = np.array(non_image_top)
            non_image_bottom = np.array(non_image_bottom)

        if len(image) < 1:
            image = None
            print("Pluto WARNING - At least one return from images() is empty.")
        
        if non_images: return image, non_image_top, non_image_bottom
        return image

class Bild(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)

class Spiegel(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
        self.headline = False
        self.subtitle = False
    
    def analyse(self, img=None):
        if img is None: img = self.img
        
        category, header, bottom = self.split()
        
        date_img = self.bottom(bottom)
        
        headline_img, subtitle_img = self.header_split(header)
        
        headline = self.ocr_cleanup(self.ocr(headline_img))
        subtitle = self.ocr_cleanup(self.ocr(subtitle_img))
        date = self.ocr_cleanup(self.ocr(date_img))
        
        return self.ocr_cleanup(self.ocr(category)), headline, subtitle, date
    
    def split(self, img=None, display=False):
        if img is None: img = self.img
        
        image, img = self.images(img)
        
        gray = to_grayscale(img[:, :int(img.shape[1] / 2), :])
        
        header = []
        top_header = []
        bottom_header = []
        
        gray = expand_to_rows(gray, True, 10, False)
        
        pntr = 0
        pntr2 = len(gray)-1
        while gray[pntr][0] != 0:
            pntr += 1
            top_header.append(img[pntr])
        
        while gray[pntr2][0] != 0:
            pntr2 -= 1
            bottom_header.insert(0, img[pntr2])
        
        top_header = np.array(top_header)
        header = img[pntr:pntr2]
        bottom_header = np.array(bottom_header)
        
        if display:
            show_image(top_header)
            show_image(header)
            show_image(bottom_header)
        
        return top_header, header, bottom_header
    
    def header_split(self, img=None, display = False):
        if img is None: img = self.img
        
        img_og = img.copy()
        
        img = cv2.resize(to_grayscale(img), (600, 600))
        img = cv2.blur(img, (40, 40))
        if display: show_image(img)
        
        img = expand_to_rows(img, True, 100, False)
        img = iso_grayscale(img, True, 10, False, (50, 50))
        if display: show_image(img)
        
        for i in range(len(img)-1, 0, -1):
            if img[i][0] > 5: break
        
        headline = img_og[:i+20]
        subtitle = img_og[i+20:]
        
        self.headline = headline
        self.subtitle = subtitle
        
        if display:
            show_image(headline)
            show_image(subtitle)
        
        return headline, subtitle
    
    def images(self, img=None):
        if img is None: img = self.img
        
        image = []
        non_image = []
        
        for i in range(len(img)):
            pix = img[i][0]
            if pix[0] > 250 and pix[1] > 250 and pix[2] > 250:
                non_image.append(img[i])
            else: image.append(img[i])
        
        return np.array(image), np.array(non_image)
    
    def bottom(self, img=None):
        if img is None: img = self.img
        
        img_og = img.copy()
        
        img = to_grayscale(img)
        img = expand_to_rows(img, True, 200, False)
        
        out = []
        for i in range(5, len(img)):
            if img[i][0] == 0: break
        
        for j in range(i, len(img)):
            if img[j][0] == 0:
                out.append(img_og[j])
            else: break
        
        return np.array(out)

class WELT(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def analyse(self, img=None):
        if img is None: img = self.img
        
        headline_img, category_img, date_img = self.split()
        
        headline = self.ocr_cleanup(self.ocr(headline_img))
        category = self.ocr_cleanup(self.ocr(category_img))
        date = self.ocr_cleanup(self.ocr(date_img))
        
        return headline, category, date
    
    def split(self, img=None, display=True):
        if img is None: img = self.img
        
        img_og = img.copy()
        
        img = to_grayscale(img)
        show_image(img)
        
        images, img = self.images(img)
        
        img = expand_to_rows(img, True, 5, False)
        show_image(img)
        
        category = []
        date = []
        
        for i in range(len(img)):
            if img[i][0] == 0: break
            else: category.append(img_og[i])
        
        for j in range(len(img)-1, 0, -1):
            if img[j][0] == 0: break
        
        for t in range(j, 0, -1):
            if img[t][0] > 2: break
            else: date.insert(0, img_og[t])
        date.insert(0, img_og[t-1])
        
        img = img_og[i-10:t-5]
        category = np.array(category)
        date = np.array(date)
        
        if display:
            show_image(img)
            show_image(category)
            show_image(date)
        
        return img, category, date
    
    def images(self, img=None):
        if img is None: img = self.img
    
        image = []
        non_image = []
        
        for i in range(len(img)):
            if img[i][0] > 250:
                non_image.append(img[i])
            else: image.append(img[i])
        
        return np.array(image), np.array(non_image)

class Discord(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def analyse(self, img=None):
        if img is None: img = self.img
        
        img = to_grayscale(img)
        # show_image(img)
        
        iso1 = iso_grayscale(img.copy(), False, 240)
        # show_image(iso1)
        
        iso1 = expand_to_rows(iso1, True, 100)[:,:10]
        # show_image(iso1)
        slices = self.slice_chat(img, iso1)
        out = []
        
        for i in slices:
            info, body = self.split(i)
            name, info = self.nameinfo(info)
            name_ocr = self.ocr_cleanup(self.ocr(name))
            info_ocr = self.ocr_cleanup(self.ocr(info))
            body_ocr = self.ocr_cleanup(self.ocr(body))
            # show_image(name)
            # show_image(info)
            # show_image(body)
            out.append([name_ocr, info_ocr, body_ocr])
        
        return out
    
    def to_json(self, img=None, path=None):
        if img is None: img = self.img.copy()
        import json
        msg = self.analyse(img)
        
        jasoon = {  "source": "Discord",
                    "category": "Chat",
                    "messages": msg
                }
        
        if path == None: return json.dumps(jasoon)
        else:
            out = open(path, "w")
            json.dump(jasoon, out, indent=6)
            out.close()
    
    def remove_usericon(self, img=None):
        if img is None: img = self.img
        
        img = np.transpose(img, (1, 0))
        # show_image(img)
        img_exptr = expand_to_rows(img.copy(), True, 75)
        
        out = []
        
        for i in range(1, len(img_exptr)):
            if img_exptr[i-1][0] > 230 and img_exptr[i][0] < 230:
                out = img[i:]
                break
        
        out = np.transpose(out, (1, 0))
        return out
    
    def slice_chat(self, img=np.ndarray, mark=np.ndarray):
        """Slices a chat screenshot into images of one message
        """
        slices = []
        out = []
        
        for i in range(2, len(mark)):
            if mark[i][0] > 250 and mark[i-1][0] < 5:
                slices.append(i)
        
        for i in range(1, len(slices)):
            temp = img[slices[i-1]:slices[i]]
            temp = self.remove_usericon(temp)
            # print(type(temp))
            # show_image(temp)
            
            out.append(temp)
        
        return out
    
    def split(self, img=None):
        """Splits a chat slice into header (username, date) and content (text)
        """
        if img is None: img = self.img
        
        img_og = img.copy()
        img = expand_to_rows(img[:,:int(img.shape[1] / 2)], False, 250)
        
        for i in range(1, len(img)):
            if img[i-1][0] > 230 and img[i][0] < 230:
                img = img_og[:i]
                img2 = img_og[i:]
                break
        
        # show_image(img)
        # show_image(img2)
        
        return img, img2
    
    def nameinfo(self, img=None):
        """Splits the info part of a chat slice into name and date (info) parts 
        """
        if img is None: img = self.img
        
        middle = int((img.shape[0] + 0.5) / 2)
        name = None
        info = None
        
        for i in range(len(img[0])-5, 0, -1):
            for h in range(len(img)):
                if img[h][i] > 150:
                    # print(i, h)
                    name = img[:,:i+5]
                    info = img[:,i+5:]
                    return name, info

class FBM(PlutoObject):
    def __init__(self, img: np.ndarray):
        super().__init__(img)
    
    def analyse(self, img=None):
        if img is None: img = self.img
        
        # show_image(cv2.resize(img, (500, 500)))
        
        dim = img.shape
        gray = to_grayscale(img.copy())
        
        slices = []
        for i in range(1, len(gray)):
            if (gray[i][int(dim[1] / 4)] < 5 and gray[i-1][int(dim[1] / 4)] > 5) or \
            (gray[i][int(dim[1] / 4)] > 5 and gray[i-1][int(dim[1] / 4)] < 5) or \
            (gray[i][int(dim[1] / 5 * 4)] > 5 and gray[i-1][int(dim[1] / 5 * 4)] < 5) or \
            (gray[i][int(dim[1] / 5 * 4)] < 5 and gray[i-1][int(dim[1] / 5 * 4)] > 5): slices.append(i)
        
        slices.append(len(gray)-1)
        print(slices)
        msg = []
        
        for i in range(1, len(slices), 1):
            the_slice = (gray[slices[i-1] : slices[i]])
            the_slice = self.row_filter_recived(the_slice)
            if the_slice is not None:
                # show_image(the_slice)
                try:
                    message = self.ocr_cleanup(self.ocr(the_slice))
                    sor = self.send_or_recived(the_slice)
                    if sor == 0: continue
                    elif sor == 1: msg.append(["send", message])
                    else: msg.append(["received", message])
                except Exception: pass
        # print(msg)
        return msg
    
    def row_filter_recived(self, image=None, value=250):
        """
        Args:
            image: An grayscale image as np.ndarray, which represents a mask.
        
        Returns:
            A np.ndarray of the edited image.
        """
        dimensions = image.shape
        imglen = dimensions[0]
        out = []
        for i in range(int(imglen)):
            for j in range(dimensions[1]):
                if image[i][j] > value:
                    out.append(image[i])
                    break
        out = np.array(out)
        if out.shape[0] < 1 or out.shape[1] < 1: return None
        else:
            middle = int(out.shape[0] / 2)
            for i in range(len(out[0])-1, 11, -1):
                if out[middle][i] > 10: break
            for j in range(len(out[0])):
                if out[middle][j] > 10:
                    return out[:,j:i]
        # return out
    
    def send_or_recived(self, img=None):
        """Send or Recived? 0 for invalid, 1 for send, 2 for recived
        """
        if img is None: img = self.img
        
        img_exptr = np.transpose(img.copy(), (1, 0))
        img = np.transpose(img, (1, 0))
        img_exptr = expand_to_rows(img_exptr, True, 250)
        # show_image(img_exptr)
        
        out = []
        for i in range(len(img_exptr)):
            if img_exptr[i][0] > 250: out.append(img[i])
        out = np.array(out)
        # show_image(out)
        
        out = np.reshape(out, (-1))
        avg, num = 0, 0
        for pixval in out:
            if pixval > 200: continue
            else:
                avg += pixval
                num += 1
        
        if avg / num < 48: return 0
        elif avg / num > 95: return 1
        else: return 2
    
    def to_json(self, img=None, path=None):
        if img is None: img = self.img.copy()
        import json
        msg = self.analyse(img)
        
        jasoon = {  "source": "Chat",
                    "messages": msg
                }
        
        if path == None: return json.dumps(jasoon)
        else:
            out = open(path, "w")
            json.dump(jasoon, out, indent=6)
            out.close()