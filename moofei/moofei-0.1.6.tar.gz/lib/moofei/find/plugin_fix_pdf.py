#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''
#python -m pip install pdfminer.six　
#https://dzone.com/articles/exporting-data-from-pdfs-with-python

import warnings
import os
import zlib

try:
    from pdfminer.converter import TextConverter
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.pdfpage import PDFPage 
    import pdfminer    
except ImportError:
    warnings.warn('Please Import pdfminer.six TO pip')
    pdfminer = None
    PDFPage  = None
    
try:
    import PyPDF2
except ImportError:
    warnings.warn('Please Import PyPDF2 TO pip')
    PyPDF2 = None    

try:
    from .cplugin_fix import _StringIO, StringIO, cPlugin_Fix  
except (ImportError,ValueError):
    from cplugin_fix import _StringIO, StringIO, cPlugin_Fix     
from moofei._find import _py, _strtypes,_find_func,_search_func


__all__ = ['Plugin_Fix_Pdf','create_image_watermark_pdf', 'create_text_watermark_pdf']


# 制作图片水印pdf
def create_image_watermark_pdf(*args, **awgs):
    from moofei._pdf import _Pdf 
    return _Pdf.create_image_watermark_pdf(*args, **awgs)
    
def create_text_watermark_pdf(*args, **awgs):
    from moofei._pdf import _Pdf 
    return _Pdf.create_text_watermark_pdf(*args, **awgs)

    
class Plugin_Fix_Pdf(cPlugin_Fix):
    def is_enable(self):
        return pdfminer or PyPDF2
        
    def pass_mark(self, out_path, user_pwd="", owner_pwd="", mark_path=None):
        '''
        pdfpath = Plugin_Fix_Pdf(pdfpath).pass_mark()
        '''
        #pip install PyPDF2 #(or PyPDF4)
        #pypdf2如下路径，有一个pdf.py 找到P=-1(默认)，修改为P=-3904(不允许打印, -44可以允许打印)
        from PyPDF2 import PdfFileReader, PdfFileWriter
        pdf_reader = PdfFileReader(self.fp or self.fpath)
        if pdf_reader.getIsEncrypted(): #print('该PDF文件被加密了.')
            try:
                pdf_reader.decrypt('') # 尝试用空密码解密
            except Exception as e:
                return False
                
        pdf_writer = PdfFileWriter()
        if mark_path:
            pdf_mark_page = PdfFileReader(mark_path).getPage(0)
            #通过迭代将水印添加到原始pdf的每一页
            for page_num  in range(pdf_reader.numPages):
                #page = add_watermark(pdf_mark, pdf_reader.getPage(page_num))
                page = pdf_reader.getPage(page_num)
                page.mergePage(pdf_mark_page)
                page.compressContentStreams()  # 压缩内容
                #将合并后的即添加了水印的page对象添加到pdfWriter
                pdf_writer.addPage(page)
        else:
            pdf_writer.appendPagesFromReader(pdf_reader)
        #pdf_writer.addMetadata({'/Author':"", '/Title':'', '/Subject':'', '/Keywords':''})
        if user_pwd or owner_pwd:
            pdf_writer.encrypt(user_pwd=user_pwd, owner_pwd=owner_pwd or user_pwd)
        pdf_writer.write(open(out_path,'wb'))
        return True
    
    @classmethod    
    def image2pdf(self, out_pdf, img_paths, mark_path=None, mark_pos=None, auto_rotate=True):
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from PIL import Image
        def getTmpImage(path, suffix='.png'):
            import tempfile
            fp = tempfile.NamedTemporaryFile(delete=False,suffix=suffix) # 
            fp.write(open(path, 'rb').read())
            return fp.name
            
        #(w, h) = landscape(A4)
        w,h = A4
        #w, h = 20 * cm, 25 * cm
        pdf = canvas.Canvas(out_pdf, pagesize=(w, h))
        # for img in os.listdir(image_path)
        for img in img_paths: 
            pdf.setFillAlpha(1) #图片透明度 0透明 1不透明
            im = Image.open(img)
            (_w, _h) = im.size
            tempPath = None
            if auto_rotate and (h>w and  _w>_h ): #还需判断是否需要旋转90度
                #im = im.rotate(90)
                im = im.transpose(Image.ROTATE_90)
                img = tempPath = getTmpImage(img)
                _h, _w = _w, _h
                im.save(img, format='png')
                #im.save(img)
                im.close()
                    
            if _w*1.0/_h < w*1.0/h: 
                hx = h 
                wx = h*_w/_h
            else:
                wx = w 
                hx = w*_h/_w    
            pdf.drawImage(img, 0,0, wx, hx) #添加图片 或者水印
            #pdf.drawImage(img, 0,0) #添加图片 或者水印
            #pdf.drawImage(f, 0, 0, w, h)
            if mark_path and  mark_pos:
                pdf.setFillAlpha(0.1)
                pdf.drawImage(mark_path, *mark_pos)    
            pdf.showPage() #换页
            
            try:
                os.remove(tempPath)
            except:
                pass
                
        pdf.save()
        
    def magick_pdf2png(self, out_dir):
        import PythonMagick
        from PyPDF2 import PdfFileReader, PdfFileWriter
        pdf_reader = PdfFileReader(self.fp or self.fpath)
        if pdf_reader.isEncrypted:
            pdf_reader.decrypt('')
        fpath = self.get_tempfile_or_path()
        for page_num  in range(pdf_reader.numPages):
            page = fpath + '[' + str(page_num) +']'
            im = PythonMagick.Image(page) #PythonMagick.Image()   
            im.density('300')# im.density=300
            #im.read(page)
            out_path = os.path.join(out_dir, str(page_num)+'.png')
            im.write(out_path)
            
    def fitz_pdf2png(self, out_dir=None, to_txt=False):  
        import fitz
        fitz_path = self.get_tempfile_or_path(suffix=True)
        doc = fitz.open(fitz_path)
        Ls = []
        if not to_txt and not out_dir: out_dir="./" 
        for pg in range(doc.pageCount):
            page = doc[pg]
            rotate = int(0)
            zoom_x = 2.0
            zoom_y = 2.0
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pm = page.getPixmap(matrix=trans, alpha=False)
            if out_dir:
                fpath = os.path.join(out_dir, '%s.png'%pg)
            else:
                fpath = self.get_tempfile_fix_path('.png')
            pm.writePNG(fpath)
            #text = page.getText() #text = page.getText(output='rawdict')
            #print(text)
            if to_txt:
                txt = self.image2txt(fpath=fpath,
                                     fp = None, #Image.open(io.BytesIO(data)),
                                     frombox = ' -> '.join([self.frombox or '',  '%s.png'%pg])
                                     )
                Ls.append(txt)
                if not out_dir:
                    os.remove(fpath)
            else:
                Ls.append(fpath)
        if to_txt:
            Ls = ''.join(Ls)
        return Ls
        
    def extract_image(self, out_dir=None, to_txt=False):
        import PyPDF2, io
        from  PyPDF2 import generic
        from PIL import Image
        Ls = []
        if not to_txt and not out_dir: out_dir="./" 
        if self.fp: self.fp.seek(0)
        pdf_reader = PyPDF2.PdfFileReader(self.fp or open(self.fpath, "rb"))
        if pdf_reader.isEncrypted:
            pdf_reader.decrypt('')
        for i in range(0, pdf_reader.getNumPages()):
            page = pdf_reader.getPage(i)
            try:
                xObject = page['/Resources']['/XObject'].getObject()
            except KeyError:
                xObject = []
            #table = page.extract_table(table_setting={})
            #for t in table: 
            #print(page.extractText().encode('latin-1').decode('gb18030'), '~~~') #不支持中文
            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    try:
                        color_space = xObject[obj]['/ColorSpace']
                        if ColorSpace == '/DeviceRGB':
                            mode = "RGB"
                        elif ColorSpace == '/DeviceCMYK':
                            mode = "CMYK"
                            # will cause errors when saving
                        elif ColorSpace == '/DeviceGray':
                            mode = "P"
                        elif isinstance(cspace, generic.ArrayObject) and cspace[0] == '/ICCBased':
                            color_map = obj['/ColorSpace'][1].getObject()['/N']
                            if color_map == 1:
                                mode = "P"
                            elif color_map == 3:
                                mode = "RGB"
                            elif color_map == 4:
                                mode = "CMYK"
                        else:
                            mode = "RGB"        
                    except:
                        mode = "RGB"
                        print('No /ColorSpace', self.fpath)
                    #if isinstance(color_space, pdf.generic.ArrayObject) and color_space[0] == '/Indexed':
                    #    color_space, base, hival, lookup = [v.getObject() for v in color_space] # pg 262
                    #    mode = img_modes[color_space]
        
                    try:
                        data = xObject[obj].getData() #
                    except:
                        data = xObject[obj]._data
                        if xObject[obj]['/Filter'] == '/FlateDecode':
                            data = zlib.decompress(data)
                            
                    
                    '''
                    if '/Filter' in xObject[obj]:
                        if xObject[obj]['/Filter'] == '/FlateDecode':
                            img = Image.frombytes(mode, size, data)
                            img.save(obj[1:] + ".png")
                        elif xObject[obj]['/Filter'] == '/DCTDecode':
                            img = open(obj[1:] + ".jpg", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/JPXDecode':
                            img = open(obj[1:] + ".jp2", "wb")
                            img.write(data)
                            img.close()
                        elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                            img = open(obj[1:] + ".tiff", "wb")
                            img.write(data)
                            img.close()
                        elif '/LZWDecode' in xObject[obj]['/Filter'] :
                            img = open(fn + ".tif", "wb")
                            img.write(data)
                            img.close()
                    else:
                        img = Image.frombytes(mode, size, data)
                        img.save(obj[1:] + ".png")
                    '''
                    fpath = ""
                    if xObject[obj]['/Filter'] == '/FlateDecode': #file_stream=zlib.decompress(file_stream).strip(b'\r\n')
                        #data = zlib.decompress(data)
                        img = Image.frombytes(mode, size, data)
                        #if color_space == '/Indexed':
                        #    img.putpalette(lookup.getData())
                        #    img = img.convert('RGB')
                        _fname = obj[1:]+'.png'
                        if out_dir:
                            fpath = os.path.join(out_dir, _fname)
                        else:
                            fpath = self.get_tempfile_fix_path('.png')
                        img.save(fpath)
                        
                    elif xObject[obj]['/Filter'] == '/DCTDecode':
                        _fname = obj[1:]+'.jpg'
                        if out_dir:
                            fpath = os.path.join(out_dir, _fname)
                        else:
                            fpath = self.get_tempfile_fix_path('.jpg')
                        img = open(fpath, "wb")
                        img.write(data)
                        img.close()
                        
                    elif xObject[obj]['/Filter'] == '/JPXDecode':
                        _fname = obj[1:]+'.jp2'
                        if out_dir:
                            fpath = os.path.join(out_dir, _fname)
                        else:
                            fpath = self.get_tempfile_fix_path('.jp2')    
                        img = open(fpath, "wb")
                        img.write(data)
                        img.close()
                        
                    elif xObject[obj]['/Filter'] == '/CCITTFaxDecode':
                        _fname = obj[1:]+'.tiff'
                        if out_dir:
                            fpath = os.path.join(out_dir, _fname)
                        else:
                            fpath = self.get_tempfile_fix_path('.tiff')   
                            
                        """
                        The  CCITTFaxDecode filter decodes image data that has been encoded using
                        either Group 3 or Group 4 CCITT facsimile (fax) encoding. CCITT encoding is
                        designed to achieve efficient compression of monochrome (1 bit per pixel) image
                        data at relatively low resolutions, and so is useful only for bitmap image data, not
                        for color images, grayscale images, or general data.

                        K < 0 --- Pure two-dimensional encoding (Group 4)
                        K = 0 --- Pure one-dimensional encoding (Group 3, 1-D)
                        K > 0 --- Mixed one- and two-dimensional encoding (Group 3, 2-D)
                        """
                        if xObject[obj]['/DecodeParms']['/K'] == -1:
                            CCITT_group = 4
                        else:
                            CCITT_group = 3
                        width = xObject[obj]['/Width']
                        height = xObject[obj]['/Height']
                        data = xObject[obj]._data  # sorry, getData() does not work for CCITTFaxDecode
                        img_size = len(data)
                        tiff_header = tiff_header_for_CCITT(width, height, img_size, CCITT_group)
                        with open(fpath, 'wb') as img_file:
                            img_file.write(tiff_header + data)
                        #
                        # import io
                        # from PIL import Image
                        # im = Image.open(io.BytesIO(tiff_header + data))
                        
                    if to_txt :
                        if fpath:
                            txt = self.image2txt(fpath=fpath,
                                                 fp = None, #Image.open(io.BytesIO(data)),
                                                 frombox = ' -> '.join([self.frombox or '',  _fname])
                                                 )
                            Ls.append(txt)
                            if not out_dir:
                                os.remove(fpath)
                    else:
                        Ls.append(fpath)    
                #else:
                #    print(xObject[obj])
            
        if to_txt:
            Ls = ''.join(Ls)
        return Ls
        
    def pypdf2text(self): #原始代码不兼容GBK
        from PyPDF2 import PdfFileReader, PdfFileWriter
        pdf_reader = PdfFileReader(self.fp or self.fpath)
        if pdf_reader.isEncrypted:
            pdf_reader.decrypt('')
        Ls = []
        for i in range(0, pdf_reader.getNumPages()):
            text = pdf_reader.getPage(i).extractText()
            Ls.append(text)
        text = '\n'.join(Ls)
        return text

        
    def all_texts(self):
        if pdfminer:
            Ls = []        
            for page in PDFPage.get_pages(self.fp  or open(self.fpath,'rb'),  caching=True,check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = _StringIO() if _py[0] == 2 else StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
                Ls.append(text)     
                converter.close()
                fake_file_handle.close()    
            text = '\n'.join(Ls)
        elif PyPDF2:
            text = self.pypdf2text()
        else:    
            try:
                import fitz
                text = fitz_pdf2png(self, out_dir=None, to_txt=False)
            except:
                warnings.warn('Please Import fitz TO pip')
                text = ""
        #print(text)
        return text
        
        
