# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vktools']

package_data = \
{'': ['*'],
 'vktools': ['.git/*',
             '.git/hooks/*',
             '.git/info/*',
             '.git/logs/*',
             '.git/logs/refs/heads/*',
             '.git/logs/refs/remotes/origin/*',
             '.git/objects/pack/*',
             '.git/refs/heads/*',
             '.git/refs/remotes/origin/*']}

setup_kwargs = {
    'name': 'vktools',
    'version': '1.0.3',
    'description': 'https://github.com/Fsoky/vktools',
    'long_description': '# vktools\n__Инструменты для удобной работы с vk_api__\n\n### Все нужные импорты\n![example imports](https://github.com/Fsoky/vktools/blob/main/images/Screenshot_0.png)\n\n### Keyboard\n\n```py\nfrom vktools import Keyboard, ButtonColor, Text, OpenLink, Location # Еще имеются VkApps, VkPay\n\nkeyboard = Keyboard(\n\t[\n\t\t[\n\t\t\tText("RED", ButtonColor.NEGATIVE),\n\t\t\tText("GREEN", ButtonColor.POSITIVE),\n\t\t\tText("BLUE", ButtonColor.PRIMARY),\n\t\t\tText("WHITE")\n\t\t],\n\t\t[\n\t\t\tOpenLink("YouTube", "https://youtube.com/c/Фсоки"),\n\t\t\tLocation()\n\t\t]\n\t]\n)\n\nvk.messages.send(user_id=event.user_id, message="Test Keyboard", keyboard=keyboard.add_keyboard())\n```\n![example keyboard](https://github.com/Fsoky/vktools/blob/main/images/Screenshot_1.png)\n\n![example code of keyboard](https://github.com/Fsoky/vktools/blob/main/images/Screenshot_3.png)\n\n### Карусели (*template*)\n\n```py\nfrom vktools import Keyboard, ButtonColor, Carousel, Element\n\ncarousel = Carousel(\n\t[\n\t\tElement(\n\t\t\t"Title 1",\n\t\t\t"Description 1",\n\t\t\t"-203980592_457239030", # photo_id\n\t\t\t"https://vk.com/fsoky", # redirect url, if user click on element\n\t\t\t[Text("Button 1", ButtonColor.POSITIVE)]\n\t\t),\n\t\tElement(\n\t\t\t"Title 2",\n\t\t\t"Description 2",\n\t\t\t"-203980592_457239030", # photo_id\n\t\t\t"https://vk.com/fsoky", # redirect url, if user click on element\n\t\t\t[Text("Button 2", ButtonColor.PRIMARY)]\n\t\t)\n\t]\n)\n\nvk.messages.send(user_id=event.user_id, message="Test Keyboard", template=carousel.add_carousel())\n```\n\n![example carouseles](https://github.com/Fsoky/vktools/blob/main/images/Screenshot_2.png)\n\n![example code of carouseles](https://github.com/Fsoky/vktools/blob/main/images/Screenshot_4.png)\n\n## Example code\n\n```py\nimport vk_api\nfrom vk_api.longpoll import VkLongPoll, VkEventType\n\nfrom vktools import Keyboard, ButtonColor, Text, OpenLink, Location, Carousel, Element\n\nvk = vk_api.VkApi(token="token")\n\n\ndef send_message(user_id, message, keyboard=None, carousel=None):\n\tvalues = {\n\t\t"user_id": user_id,\n\t\t"message": message,\n\t\t"random_id": 0\n\t}\n\n\tif keyboard is not None:\n\t\tvalues["keyboard"] = keyboard.add_keyboard()\n\tif carousel is not None:\n\t\tvalues["template"] = carousel.add_carousel()\n\n\tvk.method("messages.send", values)\n\t\n\nfor event in VkLongPoll(vk).listen():\n\tif event.type == VkEventType.MESSAGE_NEW and event.to_me:\n\t\ttext = event.text.lower()\n\t\tuser_id = event.user_id\n\n\t\tif text == "test":\n\t\t\tkeyboard = Keyboard(\n\t\t\t\t[\n\t\t\t\t\t[\n\t\t\t\t\t\tText("RED", ButtonColor.NEGATIVE),\n\t\t\t\t\t\tText("GREEN", ButtonColor.POSITIVE),\n\t\t\t\t\t\tText("BLUE", ButtonColor.PRIMARY),\n\t\t\t\t\t\tText("WHITE")\n\t\t\t\t\t],\n\t\t\t\t\t[\n\t\t\t\t\t\tOpenLink("YouTube", "https://youtube.com/c/Фсоки"),\n\t\t\t\t\t\tLocation()\n\t\t\t\t\t]\n\t\t\t\t]\n\t\t\t)\n\n\t\t\tsend_message(user_id, "VkTools Keyboard by Fsoky ~", keyboard)\n\n\t\telif text == "test carousel":\n\t\t\tcarousel = Carousel(\n\t\t\t\t[\n\t\t\t\t\tElement(\n\t\t\t\t\t\t"Title 1",\n\t\t\t\t\t\t"Description 1",\n\t\t\t\t\t\t"-203980592_457239030", # photo_id\n\t\t\t\t\t\t"https://vk.com/fsoky", # redirect url, if user click on element\n\t\t\t\t\t\t[Text("Button 1", ButtonColor.POSITIVE)]\n\t\t\t\t\t),\n\t\t\t\t\tElement(\n\t\t\t\t\t\t"Title 2",\n\t\t\t\t\t\t"Description 2",\n\t\t\t\t\t\t"-203980592_457239030", # photo_id\n\t\t\t\t\t\t"https://vk.com/fsoky", # redirect url, if user click on element\n\t\t\t\t\t\t[Text("Button 2", ButtonColor.PRIMARY)]\n\t\t\t\t\t)\n\t\t\t\t]\n\t\t\t)\n\n\t\t\tsend_message(user_id, "VkTools Carousel by Fsoky ~", carousel=carousel)\n```\n',
    'author': 'Fsoky',
    'author_email': 'cyberuest0x12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
