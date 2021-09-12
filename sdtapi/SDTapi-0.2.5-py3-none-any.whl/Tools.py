# from Scripts.cut import field_cut_tif,get_shp_field
from .Scripts import cut
# from Scripts.water_extract import GF1_wfv,landset8,GF1,band_merge
from .Scripts import WaterExtract
from .Scripts import down
from .Scripts import transform
from .Scripts import ShpSmoothness
from .Scripts import LandsatLayerStack
from .Scripts import SVMSupervisedClassification
from .Scripts import ZonalStatistics
from .Scripts import AdjoinParcels
from .Scripts import CutByShp
from .Scripts import Block
from .Scripts import AutoWriteXML
from .Scripts import SentinelDown
from .Scripts import SentinelToTif
from .Scripts import OutJpg
from .Scripts import Vector2Raster
from .Scripts import Raster2Vector
from .Scripts import ThresholdSeg
import os
import shutil


class CTool():
    def __init__(self) -> None:
        pass

    # 获取字段列表
    @classmethod
    def getShpField(cls, shpPath):
        return cut.get_shp_field(shpPath)

    # 裁剪
    @classmethod
    def cutTif(cls, shpPath, tifPath, outDir, fieldName):
        cut.field_cut_tif(shpPath, tifPath, outDir, fieldName)

    # 水体提取
    @classmethod
    def extract(cls, tifDir, sampleType, tempDir, outDir):
        if not os.path.exists(tempDir):
            os.mkdir(tempDir)
        else:
            shutil.rmtree(tempDir)
            os.mkdir(tempDir)
        WaterExtract.GF1_wfv(tifDir, sampleType, tempDir, outDir)


    # Landsat8遥感影像下载
    @classmethod
    def downloadData(cls, shpPath, type, username, password, start_date, end_date, cloud_max, output_dir):
        # type 暂时只支持landsat8
        down.landsat8_download(
            shpPath, type, username, password, start_date, end_date, cloud_max, output_dir)

    # 投影转换
    @classmethod
    def transform(cls, inDir, OutDir):
        transform.prj_change(inDir, OutDir)

    # shp平滑
    @classmethod
    def shpSmoothness(cls,shpPath, OutDir, OutName, smoothSize):
        ShpSmoothness.smooth(shpPath, OutDir, OutName, smoothSize)

    # Landsat波段合成
    @classmethod
    def landsatLayerStack(cls,imageBand, outDir):
        LandsatLayerStack.one_image_index(imageBand, outDir)

    # SVM监督分类
    @classmethod
    def supervisedClassificationSVM(cls,landcover, class_num, sample_path, ready_classified, sample_txt_path,
                                                               output_path):
        SVMSupervisedClassification.classified_SVM_band4_multi(landcover, class_num, sample_path, ready_classified, sample_txt_path,
                                                               output_path)

    # 分区统计
    @classmethod
    def zonalStatistics(cls,shpPath,tifPath,outDir):
        ZonalStatistics.field_cut_tif(shpPath,tifPath,outDir)

    # 批量将影像四至写入shp
    @classmethod
    def adjoinParcels(cls,shpDir):
        shp=shpDir
        classs = os.listdir(shp)
        for idx, folder in enumerate(classs):
            if folder.endswith('shp'):
                ori_shp = os.path.join(shp, folder)
                print(ori_shp)
                AdjoinParcels.tuban_zhongxin(ori_shp)

    # 按shp的几何形状裁剪栅格
    @classmethod
    def cutByShp(cls,tifPath,shpPath,outDir):
        #依据shp创建掩膜进行对tiff文件的裁剪
        CutByShp.sha_raster(tifPath,shpPath,outDir)

    # 分块处理
    @classmethod
    def blocking(cls,tifPath,blockNum):
        Block.div_deal(tifPath, blockNum)

    # 自动生成xml
    @classmethod
    def autoXml(cls,tifDir):
        path=tifDir
        classs = os.listdir(path)
        for idx, folder in enumerate(classs):
            if folder.endswith('tif') or folder.endswith('tiff'):
                print(folder)
                ori_tif = os.path.join(path, folder)
                AutoWriteXML.one_xml(ori_tif)
        
    # 哨兵自动下载
    @classmethod
    def sentinelDown(cls,csvPath):
        pass
        # outputDir = 
        # queryResult = 
        # successResult = 
        # startDate = 
        # endDate = 
        # productType = 
        # filename= csvPath
        # loc_data=SentinelDown.read_csv(filename)
        # test=list(loc_data)
        # for i in range(0,len(test)):
        #     id = test[i][0]
        #     name = test[i][1]
        #     wkt = test[i][2]
        #     print(id)
        #     print(name)
        #     SentinelDown.download(wkt,id,name)
    
    # 哨兵2批量转tif
    @classmethod
    def sentinelToTif(cls,safePath,outDir):
        import glob
        SAFE_Path = safePath
        out = outDir
        name = os.path.basename(SAFE_Path).split('.')[0]
        data_list = glob.glob(SAFE_Path)
        for i in range(len(data_list)):
            data_path = data_list[i]
            filename = data_path + "\\MTD_MSIL2A.xml"
            SentinelToTif.S2tif(filename,out,name)
            print(data_path + "-----转tif成功")
        print("----转换结束----")

    # 同级输出快视图
    @classmethod
    def outJpg(cls,tifDir):
        OutJpg.jpg_out(tifDir)

    # 矢量转栅格
    @classmethod
    def vector2Raster(cls,shpPath,templatePath,outDir,field,nodata):
        Vector2Raster.shp2Raster(shpPath,templatePath,outDir,field,nodata)

    # 栅格转矢量
    @classmethod
    def raster2Vector(cls,rasterPath,outDir):
        #  影像路径
        rasterfile = r"D:\gee_data\自然资源评价\分类文件\巴彦淖尔\2010_2020.tif"
        #  输出路径
        shapefile= r"D:\gee_data\自然资源评价\分类文件\变化专题"
        #  矢量名称
        name='ba2010_2020'
        Raster2Vector.raster_to_shape(rasterPath, outDir)
        
    # 阈值分割
    @classmethod
    def thresholdSeg(cls,tifPath,ouDir,threshold):
        import cv2
        import numpy as np
        path = tifPath
        out = ouDir
        #设置阈值
        thresh=threshold
        #tif转jpg并灰度化
        img = ThresholdSeg.tif_jpg(path).astype(np.uint8)
        image_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        #高斯滤波
        img_blur = cv2.GaussianBlur(image_gray , (5, 5), 5)
        # 阈值提取
        img_blur[img_blur > thresh] = 255
        img_blur[img_blur<=  thresh] =1
        ThresholdSeg.write_tiff(path, img_blur, out)
            