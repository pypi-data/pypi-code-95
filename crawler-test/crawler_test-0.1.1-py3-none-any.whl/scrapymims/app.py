from flask import Flask
from endpoints import configure_endpoints

app = Flask(__name__)

configure_endpoints(app)

if __name__ == '__main__':
    app.run(host="localhost", debug = True)
