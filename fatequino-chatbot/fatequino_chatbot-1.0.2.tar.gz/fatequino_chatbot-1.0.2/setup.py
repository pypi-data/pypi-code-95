from setuptools import setup
from pathlib import Path

long_description = """
# [Interação](https://fatequino.com.br/construcao-do-fatequino/interacao/)

This project's module goal is to develop a chatbot that can provide information about Fatec Carapicuíba's university to the user. If you have any difficulty installing the required software, please check the documentation at the "README_COMPLIMENT" file.


## Instalation

To start Fatequino's chatbot in your machine, you'll need the following softwares:

- MongoDB, versão 4.x.x
- Python3, versão 3.7.x
- pip, versão 19.x.x

### MongoDB

MongoDB Server is the database system used by the application.

To install it, follow the official documentation: [Install MongoDb Server Community Edition](https://docs.mongodb.com/manual/administration/install-community/)

### Python3 and Pip

Python is the programming language used to develop the chatbot.

To install it, you can follow the instructions at its official website: [Install Python](https://www.python.org/downloads/)

Along with Python, you'll have the `pip` tool installed. This tool is used to manage Python application's dependencies.

## Execução

Start your MongoDB instance at the port `27017`.

Download or clone this repository (using the Git tool) and place it in a directory of your preference. For example:

* On Windows: `c:\fatequino`
* On Linux: `$HOME/fatequino`

Create an environment variable named `FLASK_APP` contaning the value `my_flask_app.py`

Using a command line tool access the chatbot's directory, for example:

* On Windows: `c:\fatequino\Interação 1`
* On Linux: `$HOME/fatequino/Interação\ 1/`


Instaçç the applications dependencies running this command on the command line: `pip install -r requirements.txt`. In case of error, maybe you should try to install the dependencies one by one.

> Note: Maybe you'll have to run the command above as system administrator (super user).

Run the `python -m flask run` command to execute the program.

After these steps, the application can be accessed using the `localhost:5000` address on your browser.

## Post data into the ChatBot

To insert updated information about Fatec in the ChatBot's database, you'll have to download or access the Postman application. For more information access https://www.postman.com/

### To insert data about the classes follow these steps:

1. In the Postman application go to 'WorkSpaces', create a new tab, set it up for "POST" and put this URL in the URL field: http://127.0.0.1:5000/aulasInfo

2. Click in "Body" and change it to "Raw" and change the "type" to "JSON"

3. In the space below, insert the JSON appendix found in the classes.json file inside the project's "Interaction 1" directory

4. Click the "Send" button to send the data to the MongoDB database.

### To insert data about classes' schedules follow these steps:

1. In the Postman application go to 'WorkSpaces', create a new tab, set it up for "POST" and put this URL in the URL field: http://127.0.0.1:5000/horarioLocal

2. Click in "Body" and change it to "Raw" and change the "type" to "JSON"

3. In the space below, insert the JSON appendix found in the classes.json file inside the project's "Interaction 1" directory

4. Click the "Send" button to send the data to the MongoDB database.

"""

setup(
    name = 'fatequino_chatbot',
    version = '1.0.2',
    author = 'Interacao I - FATEC - 6o sem ADS Noturno',
    author_email = 'gabriel.santos231@fatec.sp.gov.br',
    description = 'Chatbot of Fatequino robot, which objective is to interact with students, teachers and visitors at FATEC Carapicuíba in order to give them information about teachers location, classrooms and schedules.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license = 'MIT',
    url = 'https://github.com/spanishGab/Fatequino/tree/master/Intera%C3%A7%C3%A3o%201',
    keywords = ['CHATBOT', 'FATEC', 'PROFESSORES', 'TURMAS'],
    classifiers = [
      'Development Status :: 4 - Beta',
      'Natural Language :: Portuguese (Brazilian)',
      'License :: OSI Approved :: MIT License',
      'Intended Audience :: Education'
    ]
)
