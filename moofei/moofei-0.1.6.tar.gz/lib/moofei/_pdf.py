#!/usr/bin/python
# coding: utf-8
# editor: mufei(ypdh@qq.com tel:15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''

__all__ = ['_Pdf', ]

import sys,os,json,re,time,math
import tempfile
import traceback
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas 
#py2.6: pip2 install reportlab --no-dependencies
#py2.6: pip2 install reportlab --no-deps pillow
from PyPDF2 import PdfFileReader, PdfFileWriter

fontttf_path = os.path.join(os.path.dirname(__file__),'fonts', 'simfang.ttf')        


class _Pdf:
    @classmethod
    def create_image_watermark_pdf(cls, image_path, out_pdf, image_pos=None):
        '''# 制作图片水印pdf''' 
        if image_pos is None: image_pos = [0,0]
        w = 20 * cm
        h = 25 * cm
        pdf = canvas.Canvas(out_pdf, pagesize=(w, h))
        pdf.setFillAlpha(0.1)  # 设置透明度
        # 这里的单位是物理尺寸
        pdf.drawImage(image_path, *image_pos)
        pdf.showPage()
        pdf.save()
        
    @classmethod
    def doc2pdf(cls, doc):
        '''
        linux: yum install libreoffice*
        win32: pip install comtypes
        '''
        import subprocess

        try:
            from comtypes import client
        except ImportError:
            client = None
            
        def doc2pdf_linux(doc):
            """
            convert a doc/docx document to pdf format (linux only, requires libreoffice)
            :param doc: path to document
            """
            cmd = 'libreoffice --convert-to pdf'.split() + [doc]
            p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            p.wait(timeout=10)
            stdout, stderr = p.communicate()
            if stderr:
                raise subprocess.SubprocessError(stderr)    

        doc = os.path.abspath(doc) # bugfix - searching files in windows/system32
        if client is None:
            return doc2pdf_linux(doc)
        name, ext = os.path.splitext(doc)
        try:
            word = client.CreateObject('Word.Application')
            worddoc = word.Documents.Open(doc)
            worddoc.SaveAs(name + '.pdf', FileFormat=17)
        except Exception:
            raise
        finally:
            worddoc.Close()
            word.Quit()

    @classmethod    
    def image2pdf(cls, img_path, pagesize, out_path=None, auto_rotate=True):
        from PIL import Image
        import io
        def getTmpImage(path, suffix='.png'):
            import tempfile
            fp = tempfile.NamedTemporaryFile(delete=False,suffix=suffix) # 
            fp.write(open(path, 'rb').read())
            return fp.name
        
        w, h = pagesize
        fp = open(out_path, 'wb+') if out_path else io.BytesIO()
        pdf = canvas.Canvas(fp, pagesize=pagesize)
        
        pdf.setFillAlpha(1) #图片透明度 0透明 1不透明
        im = Image.open(img_path)
        (_w, _h) = im.size
        tempPath = None
        if auto_rotate and (h>w and  _w>_h ): #还需判断是否需要旋转90度
            #im = im.rotate(90)
            im = im.transpose(Image.ROTATE_90)
            img_path = tempPath = getTmpImage(img_path)
            _h, _w = _w, _h
            im.save(img_path, format='png')
            im.close()
                
        if _w*1.0/_h < w*1.0/h: 
            hx = h 
            wx = h*_w/_h
        else:
            wx = w 
            hx = w*_h/_w

        if w>wx:
            start_x = int((w - wx)/2) 
        else:
            start_x = 0
        pdf.drawImage(img_path, start_x,0, wx, hx) #添加图片 或者水印
        #pdf.drawImage(img_path, 0,0) #添加图片 或者水印
        #pdf.drawImage(img_path, 0, 0) #添加图片 或者水印
        #pdf.drawImage(f, 0, 0, w, h)
        #if mark_path and  mark_pos:
        #    pdf.setFillAlpha(0.1)
        #    pdf.drawImage(mark_path, *mark_pos)    
        pdf.showPage() #换页
        
        try:
            if tempPath: os.remove(tempPath)
        except:
            pass        
        pdf.save()
        return  fp  
        
    @classmethod
    def create_text_watermark_pdf(cls, content, out_pdf, fontsize=30, rgba='#00000010', ttf=None, rotate=30):
        """添加水印信息"""
        # 默认大小为21cm*29.7cm
        c = canvas.Canvas(out_pdf, pagesize=(30*cm, 30*cm))
        # 移动坐标原点(坐标系左下为(0,0))
        c.translate(10*cm, 5*cm)
        
        #注册字体
        if ttf:
            if ttf.endswith('.ttf'):
                ttf_path = ttf    
            else:
                ttf_path = ttf + '.ttf'
            ttf = ttf_path.split('/')[-1].split('.')[0]
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont(ttf, ttf_path))
            #pdfmetrics.registerFont(TTFont('simfang', 'simfang.ttf'))
            c.setFont(ttf, fontsize) #Helvetica
        else:
            # 设置字体
            c.setFont("Helvetica", fontsize) #Helvetica
            
        # 指定描边的颜色
        c.setStrokeColorRGB(0, 1, 0)
        # 指定填充颜色
        c.setFillColorRGB(0, 1, 0)
        # 旋转45度,坐标系被旋转
        c.rotate(rotate)
        # 指定填充颜色
        alpha = int(rgba[-2:].lstrip('0'))/100.0
        c.setFillColorRGB(0, 0, 0, 0.1)
        # 设置透明度,1为不透明
        # c.setFillAlpha(0.1)
        # 画几个文本,注意坐标系旋转的影响
        ss = content.split('\n')
        ssln = len(ss)
        for i in range(5):
            s = ss[i%ssln] #content
            for j in range(10):
                if i in (0,1) and j==5: continue
                if i in (1,2) and j==0: continue
                
                a=10*(i-1)
                b=5*(j-2)
                c.drawString(a*cm, b*cm, s)
            c.setFillAlpha(alpha)
        # 关闭并保存pdf文件
        c.showPage()
        c.save()
        #open(out_pdf,'w').write(c.getpdfdata())	
        return out_pdf

    @classmethod
    def watermark(cls, fpath, out_path, user_pwd="", owner_pwd="", mark_path=None, meta_data=None):
        '''
        pdfpath = Plugin_Fix_Pdf(pdfpath).pass_mark()
        '''
        #pip install PyPDF2 #(or PyPDF4)
        #pypdf2如下路径，有一个pdf.py 找到P=-1(默认)，修改为P=-3904(不允许打印, -44可以允许打印)
        if isinstance(fpath, (list,tuple)):
            fpaths = fpath
        else: #isdir
            fpaths = [fpath] #str
        pdf_writer = PdfFileWriter()
        dpi = (300.0,300.0)
        size = None
        not_pdf_num = len([1 for e in fpaths if not e.lower().endswith('.pdf')])
        if not_pdf_num:
            pdfs = [e for e in fpaths if e.lower().endswith('.pdf')]
            if pdfs:
                pdf0 = PdfFileReader(open(pdfs[0], 'rb')).getPage(0)
                #if pdf0.get('/Rotate', 0) in [90, 270]:
                #    size = pdf0['/MediaBox'][2], pdf0['/MediaBox'][3]
                #else:
                #    size = pdf0['/MediaBox'][3], pdf0['/MediaBox'][2]
                #print(pdf0['/MediaBox'])
                size = int(pdf0['/MediaBox'][2]), int(pdf0['/MediaBox'][3])
            elif not_pdf_num==len(fpaths):
                size = 595, 841
                dpi  = 72 
                
        for fpath in fpaths:
            if fpath.lower().endswith('.pdf'):
                pdf_reader = PdfFileReader(fpath)
                if pdf_reader.getIsEncrypted(): #print('该PDF文件被加密了.')
                    try:
                        pdf_reader.decrypt('') # 尝试用空密码解密
                    except Exception as e:
                        return False
                
            elif 0: #image [".png", ".jfif", ".gif", ".jpeg", ".jpg"]
                import io
                from PIL import Image 
                buf = io.BytesIO()
                img = Image.open(io.BytesIO(open(fpath,'rb').read()))
                print(img.size, img.info)
                if size:
                    img = img.resize((size[0], int(img.size[1]*size[0]/img.size[0])), Image.ANTIALIAS)
                    #img = img.resize((size[0], int(img.size[1]*size[0]/img.size[0])))
                    img.show()
                #img.convert("RGB").save(buf, format="pdf")
                img.convert("RGB").save(buf, format="pdf",dpi=dpi)
                pdf_reader = PdfFileReader(buf)
                # once image is PDF, it can be appended
                #pdf_writer.addPage(PdfFileReader(buf).getPage(0))                        
            else:
                import io
                from PIL import Image
                buf = cls.image2pdf(fpath, pagesize = size)
                pdf_reader = PdfFileReader(buf)
                    
            if mark_path:
                pdf_mark_page = PdfFileReader(mark_path).getPage(0)
                #通过迭代将水印添加到原始pdf的每一页
                for page_num  in range(pdf_reader.numPages):
                    #page = add_watermark(pdf_mark, pdf_reader.getPage(page_num))
                    page = pdf_reader.getPage(page_num)
                    try:
                        page.mergePage(pdf_mark_page)
                    except:
                        traceback.print_exc()
                    page.compressContentStreams()  # 压缩内容
                    #将合并后的即添加了水印的page对象添加到pdfWriter
                    pdf_writer.addPage(page)
                
        #pdf_writer.addMetadata({'/Author':"", '/Title':'', '/Subject':'', '/Keywords':''})
        if meta_data:
            pdf_writer.addMetadata(meta_data)
        if user_pwd or owner_pwd:
            pdf_writer.encrypt(user_pwd=user_pwd, owner_pwd=owner_pwd or user_pwd)
        pdf_writer.write(open(out_path,'wb'))
        return True
        
    @classmethod
    def watermark_word(cls, word, fpath, out_path=None, fontsize=30, rgba='#00000020', font_path=fontttf_path, rotate=30, user_pwd="", owner_pwd="", meta_data=None):
        mask_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name #
        out_path = out_path or tempfile.NamedTemporaryFile(delete=False,suffix='.pdf').name #, 
        mark_path = cls.create_text_watermark_pdf(word, mask_pdf, fontsize=fontsize, rgba=rgba, ttf=font_path, rotate=rotate)
        cls.watermark(fpath, out_path, user_pwd=user_pwd, owner_pwd=owner_pwd, mark_path=mark_path, meta_data=meta_data) 
        os.remove(mask_pdf)
        return out_path
        
    @classmethod
    def compress(cls, fpath, out_path=None):
        import fitz
        import tempfile
        _doc = fitz.open(fpath)
        doc = fitz.open()       
        for pg in range(_doc.pageCount):
            page = _doc[pg] #'get_pixmap', 'get_svg_image
            if 0 and not page.getImageList():
                #_page = _doc.convert_to_pdf(pg,pg+1)
                doc.insertPDF(fitz.open("pdf", page)) #loadPage, newPage, insert_pdf              
            else: #print(page.getImageList(),page.getText())    
                zoom = int(100)
                rotate = int(0)
                trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)
                pm = page.getPixmap(matrix=trans, alpha=False)
                fname = tempfile.NamedTemporaryFile(delete=False,suffix='.png').name
                pm.writePNG(fname)
                imgdoc = fitz.open(fname)                 # 打开图片
                pdfbytes = imgdoc.convertToPDF()        # 使用图片创建单页的 PDF
                imgpdf = fitz.open("pdf", pdfbytes)
                doc.insertPDF(imgpdf) 
                imgdoc.close()    
                os.remove(fname)
   
        if not out_path:
            out_path = tempfile.NamedTemporaryFile(delete=False,suffix='.pdf').name
        doc.save(out_path)     
        doc.close()
        _doc.close()
        return out_path
    
    @classmethod
    def compress_PDFDoc(cls, fpath, out_path=None):   
        from PDFNetPython3 import PDFDoc, Optimizer, SDFDoc, ImageSettings, MonoImageSettings,OptimizerSettings
        doc = PDFDoc(fpath)
        doc.InitSecurityHandler()
        if 0:
            mono_image_settings = MonoImageSettings()
            mono_image_settings.SetCompressionMode(MonoImageSettings.e_jbig2)
            mono_image_settings.ForceRecompression(True)

            opt_settings = OptimizerSettings()
            opt_settings.SetMonoImageSettings(mono_image_settings)
    
            Optimizer.Optimize(doc, opt_settings)
        else:
            image_settings = ImageSettings()
    
            # low quality jpeg compression
            image_settings.SetCompressionMode(ImageSettings.e_jpeg)
            image_settings.SetQuality(1)
            
            # Set the output dpi to be standard screen resolution
            image_settings.SetImageDPI(144,96)
            
            image_settings.ForceRecompression(True)
            
            opt_settings = OptimizerSettings()
            opt_settings.SetColorImageSettings(image_settings)
            opt_settings.SetGrayscaleImageSettings(image_settings)

            Optimizer.Optimize(doc, opt_settings)

        #Optimizer.Optimize(doc)
        doc.Save(out_path, SDFDoc.e_linearized)
        doc.Close()
        #doc.Save(out_path, SDFDoc.e_remove_unused)
    
    
def main(folder='./temp'):
    import webbrowser
    _Pdf.create_text_watermark_pdf('11111', './temp/temp.pdf')
    for f in os.listdir(folder):
        if not f.endswith('.pdf'): continue
        if f=='temp.pdf':continue
        fpath = os.path.join(folder,f)
        #复印或拍照无效\nMufei 800120
        opath = _Pdf.watermark_word('复印或拍照无效\nMufei 800120', fpath)
        if opath:
            webbrowser.open(opath)
        
if __name__ == "__main__":  
    import doctest
    doctest.testmod() #verbose=True 
    main()

    

