import setuptools

setuptools.setup(name='ubotadapter',
                 version='0.3.1',
                 description='Bot Adapter class',
                 url='',
                 author='Smyek',
                 author_email='smyek.job@gmail.com',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 install_requires=['backoff', 'vkale>=0.4.2', 'python-telegram-bot', 'deteefapi>=0.4.1'],
                 zip_safe=False)
