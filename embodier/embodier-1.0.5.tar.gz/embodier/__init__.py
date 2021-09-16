__author__ = '2000prath@gmail.com'

from PIL import Image,ImageEnhance,ImageOps,ImageDraw,ImageFont
import numpy as np
import random
import time

class AvatarGenerator:
    """
    obj = AvatarGenerator()\n
    img = obj.CreateAvatar(5,300,'lightgrey')\n
    str_bs64 = obj.toBase64(img)\n
    img.show() #use to open image\n
    img.save('image.png') #to save image\n

    """
    def toBase64(self,img):
        import base64
        from io import BytesIO

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue())
        return img_base64

    def getMatrix(self,x,y):
        #don't use more than 10 seconds to generate matrix
        wait_till = time.time() + 10
        ones = 0
        zeros = 1
        array=None
        while(ones<zeros and time.time() < wait_till):
            array = np.random.randint(2, size=(x, y))
            for i in range(len(array)):
                for j in range(len(array[i])):
                    if array[i][j]:
                        ones+=1
                    else:
                        zeros+=1
            for i in range(len(array)):
                if array[i][1]==1:
                    ones+=1
                else:
                    zeros+=1
                if array[i][0]==1:
                    ones+=1
                else:
                    zeros+=1
                array[i][len(array)-2] = array[i][1]
                array[i][len(array)-1] = array[i][0]
        return array


    def CreateAvatar(self,xy_axis=5,pixels=300,background_color='lightgrey',border=True,border_width=25):
        """
        @xy_axis : Row and Columns, it should be same Eg. 5 for(5*5 matrix)\n
        @pixels : Use less pixels to minimize final image siz Eg. 300 e\n
        @background_color : Specify the color of background (accepts color name, Hex code,RGB values)Eg. white, grey, lighgrey\n
        @border : Boolean - True: add border, False: no border\n
        @border_width : size
        """
        #to get the image x and y should be same
        column_row = xy_axis
        pixel_x_y = pixels
        #create blank image 
        img = Image.new('RGB', (pixel_x_y, pixel_x_y), background_color)
        #get matrix to fill blocks
        array = self.getMatrix(column_row,column_row)
        #generate colors RGB
        red = random.randint(0,255)
        green = random.randint(0,255)
        blue = random.randint(0,255)
        #generate dark color if RGB is light color
        while(red+green+blue > 400):
            red = random.randint(0,255)
            green = random.randint(0,255)
            blue = random.randint(0,255)
        for i in range(len(array)):
            for j in range(len(array[i])):
                if array[i][j] == 1: 
                    right = int(j*(pixel_x_y/column_row))
                    top = int(i*(pixel_x_y/column_row))
                    left = int((j*(pixel_x_y/column_row))+(pixel_x_y/column_row))
                    bottom = int((i*(pixel_x_y/column_row))+(pixel_x_y/column_row))
                    img.paste( (red,green,blue), [right ,top,left,bottom])
        if border:
            img = ImageOps.expand(img,border=border_width,fill=background_color)
        return img

    def TextAvatar(self,text,background_color=None):
        pixels = 300
        if not text:
            print("This function accept text, please provide a text to create image")
            return
        if len(text) != 2:
            print("************* Please provide only 2-3 latters in order to create text image *************")
            text = text[0:2]
        fontSize = 160
        centerPixel = 48
        colors = ['#808080','#800000','#808000','#FF0000','#008000','#008080','#0000FF','#000080','#FF00FF','#800080']
        if not background_color:
            background_color = random.choice(colors)
        img = Image.new('RGB', (pixels, pixels), background_color)
        I1 = ImageDraw.Draw(img)
        myFont = ImageFont.truetype('arial.ttf', fontSize)
        I1.text((centerPixel, centerPixel+15), text.upper() ,font=myFont, fill='#FDFDFD')
        return img

obj = AvatarGenerator()
obj.TextAvatar('yy')


