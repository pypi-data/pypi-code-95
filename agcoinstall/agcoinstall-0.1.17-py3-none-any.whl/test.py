from lxml import etree
from sys import stdout
from io import BytesIO

def set_edt_environment(env_base_url):
    files = [r'C:\Program Files (x86)\AGCO Corporation\EDT\AgcoGT.exe.test.config',]
    for file in files:
        root = etree.parse(file)
        for event, element in etree.iterwalk(root):
            if element.text and 'https' in element.text:
                print(element.text)
                element.text = f'https://{env_base_url}/api/v2'
                print(element.text)
        with open(file, 'wb') as f:
            f.write(etree.tostring(root, encoding='UTF-8', xml_declaration=True, pretty_print=True))



if __name__ == '__main__':
    set_edt_environment("secure.agco-ats.com")

