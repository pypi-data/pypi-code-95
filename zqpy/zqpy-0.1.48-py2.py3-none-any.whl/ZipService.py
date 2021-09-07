import zlib
import os
import zipfile
# http://api.1473.cn/LearningMaterials/Node/Node_zlib.aspx
# https://www.cnblogs.com/ManyQian/p/9193199.html

class ZipServiceClass():
    # zlib.compress 用来压缩字符串的bytes类型
    def str_compress(self, message):
        '''字符串加密'''
        bytes_message = message.encode()
        return zlib.compress(bytes_message, zlib.Z_BEST_COMPRESSION)
        
    def str_decompress(self, compressed):
        '''字符串解密'''
        return zlib.decompress(compressed)

    # zlib.compressobj 用来压缩数据流，用于文件传输 level[1-9]
    def file_compress(self, inputFile, zlibFile, level=9):
        '''文件加密'''
        infile = open(inputFile, "rb")
        zfile = open(zlibFile, "wb")
        compressobj = zlib.compressobj(level)   # 压缩对象
        data = infile.read(1024)                # 1024为读取的size参数
        while data:
            zfile.write(compressobj.compress(data))     # 写入压缩数据
            data = infile.read(1024)        # 继续读取文件中的下一个size的内容
        zfile.write(compressobj.flush())    # compressobj.flush()包含剩余压缩输出的字节对象，将剩余的字节内容写入到目标文件中
    
    def file_decompress(self, zlibFile, endFile):
        '''文件解密'''
        zlibFile = open(zlibFile, "rb")
        endFile = open(endFile, "wb")
        decompressobj = zlib.decompressobj()
        data = zlibFile.read(1024)
        while data:
            endFile.write(decompressobj.decompress(data))
            data = zlibFile.read(1024)
        endFile.write(decompressobj.flush())
    

    def get_zip_file(self, input_path, result):
        """
        对目录进行深度优先遍历
        :param input_path:
        :param result:
        :return:
        """
        files = os.listdir(input_path)
        for file in files:
            if os.path.isdir(input_path + '/' + file):
                self.get_zip_file(input_path + '/' + file, result)
            else:
                result.append(input_path + '/' + file)

    def zip_file_path(self, input_path, output_path, output_name, password):
        """
        压缩文件夹
        :param input_path: 要被压缩的文件夹路径
        :param output_path: 打出得解压包的路径
        :param output_name: 压缩包名称
        :param password: 密码
        :return:
        """
        zipfiles = zipfile.ZipFile(output_path + '/' + output_name, 'w', zipfile.ZIP_DEFLATED)
        filelists = []
        self.get_zip_file(input_path, filelists)
        for file in filelists:
            zipfiles.write(file)
        zipfiles.setpassword((password or 'zq162082').encode())
        # 调用了close方法才会保证完成压缩
        zipfiles.close()
        return output_path + r"/" + output_name

    def unzip_file_path(self, output_path, input_path, password, output_name=None):
        """
        解压缩文件夹
        :param output_path: 解压缩包的路径
        :param input_path: 压缩文件的路径
        :param password: 密码
        :param output_name: 解压缩包的名字，默认是压缩包的名字
        :return:
        """
        zipfiles=zipfile.ZipFile(input_path,'r')
        zipfiles.extractall(os.path.join(output_path,output_name or os.path.splitext(input_path)[0]),pwd=(password or 'zq162082').encode())
        zipfiles.close()


if __name__=="__main__":
    zipService = ZipServiceClass()
    #-----------------------------str---------------------------------
    print(zipService.str_compress('666666666666669'))
    print(zipService.str_decompress(zipService.str_compress('666666666666669')))
    #-----------------------------strend---------------------------------
    #-----------------------------file---------------------------------
    # 测试数据流压缩
    beginFile = "./beginFile.txt"
    zlibFile = "./zlibFile.txt"
    level = 9
    zipService.file_compress(beginFile, zlibFile, level)
 
    # 测试数据流解压
    zlibFile = "./zlibFile.txt"
    endFile = "./endFile.txt"
    zipService.file_decompress(zlibFile, endFile)
    #-------------------------------fileend------------------------------

    #-----------------------------dir---------------------------------
    zipService.zip_file_path(r"./proxy", os.getcwd(), '123.zip', '1620829248')
    zipService.unzip_file_path(os.getcwd(), '123.zip', '1620829248', '')
    #-------------------------------dirend------------------------------