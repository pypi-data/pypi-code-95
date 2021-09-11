#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['_Image', ]

import sys,os,json,re,time,math,struct  
import PIL
from PIL import Image, ImageFile, ImageDraw, ImageFont, ImageChops, ImageEnhance, ImageSequence
ImageFile.LOAD_TRUNCATED_IMAGES = True
#py2.6: pip2 install pillow==2.2.1 

from string import Template as string_Template
py = list(sys.version_info)
fontttf_path = os.path.join(os.path.dirname(__file__),'fonts', 'simfang.ttf')


class _Image:
    @classmethod
    def what(cls, file, h=None):
        import imghdr
        return imghdr.what(file, h=h)
        
    @classmethod    
    def determine_image_type (cls, stream_first_4_bytes):
        #Find out the image file type based on the magic number comparison of the first 4 (or 2) bytes#
        file_type = None
        bytes_as_hex = binascii.b2a_hex(stream_first_4_bytes)
        if bytes_as_hex.startswith(b'ffd8'):
            file_type = '.jpeg'
        elif bytes_as_hex == b'89504e47':
            file_type = '.png'
        elif bytes_as_hex == b'47494638':
            file_type = '.gif'
        elif bytes_as_hex.startswith(b'424d'):
            file_type = '.bmp'
        #tif,svg,eps,hdr
        
        return file_type 
        
    @classmethod    
    def tiff_header_for_CCITT(cls, width, height, img_size, CCITT_group=4):
        tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
        return struct.pack(tiff_header_struct,
                       b'II',  # Byte order indication: Little indian
                       42,  # Version number (always 42)
                       8,  # Offset to first IFD
                       8,  # Number of tags in IFD
                       256, 4, 1, width,  # ImageWidth, LONG, 1, width
                       257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                       258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                       259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                       262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                       273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                       278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                       279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                       0  # last IFD
                       )

    @classmethod
    def watermark_word(cls, word, fpath, out_path=None, fontsize=36, rgba='#00000036', font_path=fontttf_path, rotate=-45, meta_data=None, im=None):
        #文字水印
        try:
            im = im or Image.open(fpath)
        except : #PIL.UnidentifiedImageError
            return 
        
        try:
            text = unicode(word,'UTF-8')
        except:
            text = word
            
        if font_path and not os.path.isfile(font_path): font_path=None #'Helvetica'    
        font = font_path and ImageFont.truetype(font_path, fontsize) #50, int(20 / 1.5)
        new_img = Image.new('RGBA', (im.size[0] * 3, im.size[1] * 3), (0, 0, 0, 0))
        new_img.paste(im, im.size) # 添加背景
     
        font_len = len(text) # 添加水印
        rgba_image = new_img.convert('RGBA')
        text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
        image_draw = ImageDraw.Draw(text_overlay)

        v = int(40*fontsize/36)
        for i in range(0, rgba_image.size[0], font_len*v): #40, 100):
            for j in range(0, rgba_image.size[1], 200): #200
                image_draw.text((i, j), text, font=font,
                                #fill=(0, 0, 0, 50),
                                fill=rgba #字体颜色
                                )
        text_overlay = text_overlay.rotate(rotate)
        image_with_text = Image.alpha_composite(rgba_image, text_overlay)
        im = image_with_text.crop((im.size[0], im.size[1], im.size[0] * 2, im.size[1] * 2)) # 裁切图片
        if out_path:
            if os.path.isdir(out_path):
                out_path = out_path+'.'+ fpath.split('.')[-1]    
            if out_path.lower().endswith(('.jpg','.jpeg')):
                im=im.convert('RGB')
            im.save(out_path)
        return out_path or im                   

    @classmethod
    def verify(cls, path):
        bValid = True  
        if isinstance(path, str):
            if not os.path.isfile(path):
                return False
            f = open(path, 'rb') # 以二进制形式打开 
            is_open = True            
        elif getattr(path, 'read', None):
            f = path
            is_open = False 
        else:
            f = open(path, 'rb') # 以二进制形式打开 
            is_open = True
    
        bValid = cls.what(f)
        f.seek(0) 
        if bValid:
            try:
                Image.open(f).verify()
            except Exception as e:
                bValid = False 
            
        if is_open: f.close()    
        return bValid

    @classmethod    
    def file2png(cls, source, target):  
        Bits = 3  
        data = open(source, "rb").read()  
        fileSize = len(data)  
        data += b"\0\0\0"  
        
        # Ratio 4:3  
        width = int(math.sqrt(float(fileSize) / Bits * 4 / 3)) + 1  
        height = int((fileSize/Bits) / width) + 1  
        if width * height * Bits < fileSize: raise Exception("File Too Large")  
        if width == 0 or height == 0: raise Exception("File Too Small.")  
      
        im = Image.new("RGB", (width, height)) 
        if py[0]==2:    
            pngData = tuple(tuple(map(ord, [y for y in data[x: x+Bits]])) for x in range(0, fileSize, Bits))  
        else:
            pngData = tuple(tuple([y for y in data[x: x+Bits]]) for x in range(0, fileSize, Bits))  
        im.putdata(pngData)  
        im.save(target, "PNG", transparency=struct.unpack("B"*Bits, struct.pack("I", fileSize)[:Bits]), compression = 9)    
        im.close()
        
    @classmethod  
    def png2file(cls, source, target): 
        Bits = 3
        im = Image.open(source)     
        fileSize = struct.unpack("I",struct.pack("B"*Bits, *im.info["transparency"]) + b"\0"*(4-Bits))[0]
        data = im.tobytes()[:fileSize] 
        open(target, "wb").write(data)  
        im.close() 
    
def main(folder='./temp'):
    for f in os.listdir(folder):
        fpath = os.path.join(folder,f)
        #复印或拍照无效\nMufei 800120
        im = _Image.watermark_word('复印或拍照无效\nMufei 800120', fpath)
        if im:
            im.show()
        
if __name__ == "__main__":  
    import doctest
    doctest.testmod() #verbose=True 
    main()

    

