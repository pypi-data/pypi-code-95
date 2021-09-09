from lxml import etree
import os


def parse_xml_folder(folder_name):
    text_range = []
    p_range = []
    parser = etree.HTMLParser(encoding="utf-8")
    filename_list = os.listdir(folder_name)
    oid = ''
    for filename in filename_list:
        if '.xml' in filename:
            tree = etree.parse(".\\%s\\%s" % (folder_name, filename), parser=parser)
            text_list = tree.xpath('//d/text()')
            for text in text_list:
                text_range.append(text)
            p_list = tree.xpath('//d/@p')
            for p in p_list:
                p_range.append(p)
            oid = tree.xpath('//chatid/text()')[0]
    root = etree.Element("i")
    chatterer = etree.SubElement(root, "chatserver")
    chatterer.text = 'chat.bilibili.com'
    chatid = etree.SubElement(root, 'chatid')
    chatid.text = str(oid)
    mission = etree.SubElement(root, 'mission')
    mission.text = '0'
    maxlimit = etree.SubElement(root, 'maxlimit')
    maxlimit.text = str(len(text_range))
    real_name = etree.SubElement(root, 'real_name')
    real_name.text = '0'
    source = etree.SubElement(root, 'source')
    source.text = '0'
    for i in range(len(text_range)):
        d = etree.SubElement(root, 'd', p=p_range[i])
        d.text = text_range[i]
    tree = etree.ElementTree(root)
    tree.write('.\\%s\\%s.xml' % (folder_name, str(oid)), pretty_print=True, xml_declaration=True, encoding="utf-8")

