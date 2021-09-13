from battlenet_client.client import BattleNetClient
import flask_testing
from flask import Flask, render_template, session, redirect, request, make_response, url_for


class UserAuthClientTest(flask_testing.TestCase):

    def setUp(self):
        self.client = BattleNetClient('us', scope=['wow.profile'], redirect_uri='https://localhost:5000/callback')

    def create_app(self):
        user_auth = Flask(__name__)
        user_auth.secret_key = b'73874837483723487384'

        @user_auth.route('/')
        def index():
            return render_template('index.jinja', user_info=session.get('user_info'))

        @user_auth.route('/login')
        def login():
            page = redirect(self.client.authorization_url())
            return page

        @user_auth.route('/callback')
        def authorize():
            self.client.fetch_token()
            response = make_response(
                self.client.post(request.url, locale='enus', namespace=self.client.profile_namespace))
            return response

        @user_auth.route('/logout')
        def logout():
            if 'user_info' in session:
                del session['user_info']
            return redirect(url_for('index'))

        return user_auth

    def test_authorization_url(self):
        url = self.client.authorization_url()
        self.assertTrue(url.find('us.battle.net'))
        self.assertTrue(url.find('state'))
        self.assertTrue(url.find('code'))
        self.assertTrue(url.find('redirect_uri'))

    def test_login(self):
        pass

    def test_callback(self):
        redirect(self.client.authorization_url())
        self.assertTrue(1)

    def test_logout(self):
        pass
