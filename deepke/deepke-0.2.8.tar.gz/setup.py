from setuptools import setup, find_packages
setup(
    name='deepke',  # 打包后的包文件名
    version='0.2.8',    #版本号
    keywords=["pip", "RE"],    # 关键字
    description='DeepKE 是基于 Pytorch 的深度学习中文关系抽取处理套件。',  # 说明
    long_description="client",  #详细说明
    license="Apache-2.0 License",  # 许可
    url='https://github.com/zjunlp/deepke',
    author='ZJUNLP',
    author_email='xx2020@zju.edu.cn',
    # packages=find_packages(),     #这个参数是导入目录下的所有__init__.py包
    include_package_data=True,
    platforms="any",
    # install_requires=[
    #     'torch>=1.2',
    #     'hydra-core>=0.11',
    #     'tensorboard>=2.0',
    #     'matplotlib>=3.1',
    #     'transformers>=2.0',
    #     'jieba>=0.39',
    #     'scikit-learn>=0.22'
    # ],    # 引用到的第三方库
    # py_modules=['pip-test.DoRequest', 'pip-test.GetParams', 'pip-test.ServiceRequest',
    #             'pip-test.ts.constants', 'pip-test.ac.Agent2C',
    #             'pip-test.ts.ttypes', 'pip-test.ac.constants',
    #             'pip-test.__init__'],  # 你要打包的文件，这里用下面这个参数代替
    packages=['deepke.models', 'deepke.module', 'deepke.utils', 'deepke.tools'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
