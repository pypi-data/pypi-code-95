from flask import *
def run(version):
    app = Flask(__name__)
    @app.route('/')
    def d():
        return render_template('index.html',version=version)

    app.run(debug=True)