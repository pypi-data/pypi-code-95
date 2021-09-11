import io
import PIL
import pickle
import requests
class image():
  def __init__(self,imgpath):
    self.imgpath = imgpath

  def getmobilenet(self):
    from botnoi import mobilenet as mn
    mfeat = mn.extract_feature(self.imgpath)
    self.mobilenet = mfeat
    return mfeat

  def getresnet50(self):
    from botnoi import resnet50 as rn
    rfeat = rn.extract_feature(self.imgpath)
    self.resnet50 = rfeat
    return rfeat

  def getimage(self):
    r = requests.get(self.imgpath, allow_redirects=True, timeout=10)
    image_bytes = io.BytesIO(r.content)
    img = PIL.Image.open(image_bytes)
    self.image = img
    return img

  def getmobilenetpca(self):
    from botnoi import mobilenet as mn
    feat = self.mobilenet
    feat = pca.transform([feat])
    self.mobilenetpca = feat
    return feat




  def save(self,filename):
    pickle.dump(self,open(filename,'wb'))



