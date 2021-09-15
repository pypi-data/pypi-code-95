BLUEPRINTS = {
    'flask': {
        '__init__': {
            'db': (
                "import os"
                "\nfrom flask import Flask"
                "\nfrom flask_sqlalchemy import SQLAlchemy"
                "\nfrom flask_migrate import Migrate\n"
                "\napp = Flask(__name__)"
                "\napp.config['SECRET_KEY'] = os.getenv('SECRET_KEY')"
                "\napp.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')\n"
                "\ndb = SQLAlchemy(app)"
                "\nmigrate = Migrate(app, db)\n"
                "\nfrom app.models import *"
                "\ndb.create_all()"
                "\ndb.session.commit()\n"
                "\nfrom app import routes\n"
            ),
            'nodb': (
                "import os"
                "\nfrom flask import Flask\n"
                "\napp = Flask(__name__)"
                "\napp.config['SECRET_KEY'] = os.getenv('SECRET_KEY')\n"
                "\nfrom app import routes\n"
            ),
        },
        'wsgi': (
            "from dotenv import load_dotenv"
            "\nload_dotenv()\n"
            "\nfrom app import app\n"
            "\nif __name__ == '__main__':"
            "\n    app.run(debug=True)\n"
        ),
        'routes': {
            'db': (
                "# Create your routes here.\n"
                "\nfrom app import app, db\n"
                "\nfrom app.models import *\n"
                "\nfrom flask import Response\n"
                "\n@app.route('/')"
                "\ndef default():"
                "\n    return Response(status=200)\n"
            ),
            'nodb': (
                "# Create your routes here.\n"
                "\nfrom app import app\n"
                "\nfrom flask import Response\n"
                "\n@app.route('/')"
                "\ndef default():"
                "\n    return Response(status=200)\n"
            ),
        },
        'models': (
            "# Create your models here.\n"
            "\nfrom app import db\n"
            "\nfrom sqlalchemy import Column, Integer\n"
            "\nclass ExampleModel(db.Model):"
            "\n    id = Column(Integer, primary_key=True)\n"
        ),
        'forms': (
            "# Create your forms here.\n"
            "\nfrom flask_wtf import FlaskForm"
            "\nfrom wtforms import StringField"
            "\nfrom wtforms.validators import DataRequired\n"
            "\nclass ExampleForm(FlaskForm):"
            "\n    example_field = StringField('Example', validators=[DataRequired()])\n"
        ),
    },

    'fastapi': {
        'asgi': (
            "from dotenv import load_dotenv"
            "\nload_dotenv()\n"
            "\nfrom os import getenv"
            "\nfrom fastapi import FastAPI\n"
            "\nimport routers"
            "\nfrom db import models, DB_ENGINE\n"
            "\napp: FastAPI = FastAPI("
            "\n    debug=True if getenv('DEBUG') else False,"
            "\n    docs_url='/docs' if getenv('DEBUG') else False,"
            "\n    redoc_url='/redoc' if getenv('DEBUG') else False,"
            "\n    title=getenv('PROJECT_NAME')"
            "\n)\n"
            "\nmodels.DB_BASE.metadata.create_all(DB_ENGINE)\n"
            "\napp.include_router(routers.server.router)\n"
            "\nif __name__ == '__main__':"
            "\n    import uvicorn, psycopg2"
            "\n    uvicorn.run(app, host='127.0.0.1', port=8000) # alternatively host='localhost'\n"
        ),
        '__init__db': (
            "from os import getenv\n"
            "\nfrom sqlalchemy import create_engine"
            "\nfrom sqlalchemy.ext.declarative import declarative_base"
            "\nfrom sqlalchemy.orm import sessionmaker"
            "\nfrom sqlalchemy.orm.attributes import flag_modified\n"
            "\nuri = getenv('DATABASE_URL')"
            "\nif uri.startswith('postgres://'):"
            "\n    uri = uri.replace('postgres://', 'postgresql://', 1)\n"
            "\nif getenv('DEBUG'):"
            "\n    DB_ENGINE = create_engine(uri, connect_args={'check_same_thread': False})"
            "\nelse:"
            "\n    DB_ENGINE = create_engine(uri)"
            "\ndel uri\n"
            "\nDB_SES_LOCAL = sessionmaker(bind=DB_ENGINE)"
            "\nDB_BASE = declarative_base()\n"
            "\ndef get_db():"
            "\n    db = DB_SES_LOCAL()"
            "\n    try:"
            "\n        yield db"
            "\n    finally:"
            "\n        db.close()\n"
        ),
        'models': (
            "# Create your models here.\n"
            "\nfrom sqlalchemy import Column, Integer, String\n"
            "\nfrom db import DB_BASE\n"
            "\nclass Exacple(DB_BASE):"
            "\n    __tablename__ = 'example'\n"
            "\n    id = Column(Integer, primary_key=True, index=True)\n"
        ),
        '__init__utils': (
            "from .hashing import *\n"
        ),
        'schemas': (
            "# Create your schemas here.\n"
            "\nfrom typing import List, Optional"
            "\nfrom pydantic import BaseModel\n"
            "\nclass Example(BaseModel):"
            "\n    example_field: str\n"
        ),
        'hashing': (
            "from passlib.context import CryptContext\n"
            "\nPWD_CXT = CryptContext(schemes=['bcrypt'], deprecated='auto')\n"
            "\nclass Hash():"
            "\n    def bcrypt(password: str):"
            "\n        return PWD_CXT.hash(password)\n"
            "\n    def verify(plain_password, hashed_password):"
            "\n        return PWD_CXT.verify(plain_password, hashed_password)\n"
        ),
        '__init__routers': (
            "from os import getenv\n"
            "\nfrom fastapi import APIRouter, Depends"
            "\nfrom sqlalchemy.orm import Session\n"
            "\nfrom db import *"
            "\nfrom db.models import *\n"
            "\nfrom utils import *\n"
            "\nfrom .server import router\n"
        ),
        'server': (
            "from . import *\n"
            "\nrouter = APIRouter(tags=['Server'])\n"
            "\n@router.get('/')"
            "\ndef default():"
            "\n    return {'status': 'Live'}\n"
        ),
    },
}
