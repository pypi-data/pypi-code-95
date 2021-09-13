# Импорт недавно установленного пакета setuptools.
import setuptools

from setuptools import setup, Extension

setup(name='himod', version='0.0.1',  \
      ext_modules=[Extension('himod', ['src/hello_from_C.c'])])

# Открытие README.rst и присвоение его long_description.
with open("README.rst", "r") as fh:
	long_description = fh.read()

# Определение requests как requirements для того, чтобы этот пакет работал. Зависимости проекта.
# requirements = ["requests<=2.21.0"]

# Функция, которая принимает несколько аргументов. Она присваивает эти значения пакету.
setuptools.setup(
	# Имя дистрибутива пакета. Оно должно быть уникальным, поэтому добавление вашего имени пользователя в конце является обычным делом.
	name="hello_world_from_C",
	# Номер версии вашего пакета. Обычно используется семантическое управление версиями.
	version="0.0.1",
	# Имя автора.
	author="SVA",
	# Его почта.
	author_email="jk3ger@gmail.com",
	# Краткое описание, которое будет показано на странице PyPi.
	description="A Hello World package from C extension",
	# Тип лицензии
	license = "MIT",
	# Длинное описание, которое будет отображаться на странице PyPi. Использует README.rst репозитория для заполнения.
	long_description=long_description,
	# Определяет тип контента, используемый в long_description.
	long_description_content_type="text/markdown",
	# URL-адрес, представляющий домашнюю страницу проекта. Большинство проектов ссылаются на репозиторий.
	url="https://github.com/ericjaychi/sample-pypi-package",
	# Находит все пакеты внутри проекта и объединяет их в дистрибутив.
	packages=setuptools.find_packages(),
	# requirements или dependencies, которые будут установлены вместе с пакетом, когда пользователь установит его через pip.
	# install_requires=requirements,
	# Предоставляет pip некоторые метаданные о пакете. Также отображается на странице PyPi.
	classifiers=[
		"Programming Language :: Python :: 3.9",
		"Programming Language :: C",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	# Требуемая версия Python.
	python_requires='>=3.6',
)