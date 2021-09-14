""" Модуль хранит все параметры настройки WServer """


from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(CUR_DIR, 'photos')
TEST_PHOTO = os.path.join(PHOTOS_DIR, 'test_act_photo.png')


