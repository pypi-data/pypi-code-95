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
    }
}
