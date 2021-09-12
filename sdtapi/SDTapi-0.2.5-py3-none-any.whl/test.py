# from Tools import CTool
from YXKJapi.Tools import CTool



# print(CTool.getShpField(r"C:\Users\bmd\Documents\WeChat Files\MENGDONGx\FileStorage\File\2021-08\GF1_wfv_测试1(1)\GF1_wfv_测试1.shp"))
# """裁剪测试ok"""
# # print(CTool.getShpField(r"C:\Users\bmd\Documents\WeChat Files\MENGDONGx\FileStorage\File\2021-08\GF1_wfv_测试1(1)\GF1_wfv_测试1.shp"))
# CTool.cutTif(r"D:\鲍梦冬\shp\GF1_WFV1_E87.8_N33.0_20210711_L1A0005747273_ortho.shp",
# r"D:\鲍梦冬\影像\GF1_WFV1_E87.8_N33.0_20210711_L1A0005747273_ortho.tif",
# r"C:\Users\bmd\Desktop\test",
# "OBJECTID"

# )

"""提取测试"""
# CTool.extract(r"C:\Users\bmd\Documents\WeChat Files\MENGDONGx\FileStorage\File\2021-08\1094_cut",
# r"C:\Users\bmd\Desktop\WinForm\sample_GF.txt",
# r"C:\Users\bmd\Desktop\temp",
# r"C:\Users\bmd\Desktop\提取结果",
# "GF1_wfv")

"""下载ok"""
CTool.downloadData(r"C:\Users\bmd\Documents\WeChat Files\MENGDONGx\FileStorage\File\2021-08\GF1_wfv_测试1(1)\GF1_wfv_测试1.shp",
"landsat8",
"loney_soul",
"Zhou19960824",
"2020-05-01",
"2020-08-01",
10,
r"C:\Users\bmd\Desktop\下载测试"
)


"""投影转换ok"""
# CTool.transform(r"C:\Users\bmd\Desktop\test",r"C:\Users\bmd\Desktop\投影转换")
