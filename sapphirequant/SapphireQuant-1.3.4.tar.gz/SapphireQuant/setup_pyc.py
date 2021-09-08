import os
import shutil
import compileall

versions = ".cpython-35"
py_cache = "__pycache__"
build_dir = "build"
root = os.path.abspath('.')
print("正在编译文件...请等待...")
compileall.compile_dir(root)  # 编译
build = os.path.join(root, build_dir)
if os.path.exists(build):
    print("正在移除build目录...请等待...")
    shutil.rmtree(build)
print("正在复制文件...请等待...")
shutil.copytree(root, build)
for root, dirs, files in os.walk(build):  # 开始遍历文件
    # root 表示当前正在访问的文件夹路径
    # dirs 表示该文件夹下的子目录名list
    # files 表示该文件夹下的文件list
    # 遍历文件
    for file_name in files:
        src = os.path.join(root, file_name)
        if file_name.endswith(".py"):
            os.remove(src)
        elif file_name.endswith(".pyc"):
            upper_dir = root.replace(py_cache, "")
            dst = os.path.join(upper_dir, file_name.replace(versions, ""))
            shutil.copy(src, dst)
for root, dirs, files in os.walk(build):  # 移除缓存文件夹
    print("正在移除缓存文件...请等待...")
    if root.endswith(py_cache):
        shutil.rmtree(root)
print("打包完成...请查看目录：" + str(build))
