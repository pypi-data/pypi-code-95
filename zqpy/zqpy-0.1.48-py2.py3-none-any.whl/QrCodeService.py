from PIL import Image
import qrcode
class QrCodeServiceClass():
    def QrCode(self, codeContent, codeCoreImgPath=None, savePath=None, box_size = 8):
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=1
        )#各参数具体用法请参考底下链接
        qr.add_data(codeContent)#要显示的内容
        qr.make(fit=True)

        img = qr.make_image()
        img = img.convert("RGBA")
        if codeCoreImgPath:
            icon = Image.open(codeCoreImgPath)#打开一张图片作为二维码中心图标

            img_w, img_h = img.size
            factor = 4
            size_w = int(img_w / factor)
            size_h = int(img_h / factor)

            icon_w, icon_h = icon.size
            if icon_w > size_w:
                icon_w = size_w
            if icon_h > size_h:
                icon_h = size_h
            icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)

            w = int((img_w - icon_w) / 2)
            h = int((img_h - icon_h) / 2)

            img.paste(icon, (w, h))#将图标粘贴到二维码上
        img.save(savePath or "qrcode.png")#保存图片
