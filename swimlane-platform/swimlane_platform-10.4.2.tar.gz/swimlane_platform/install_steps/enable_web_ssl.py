from swimlane_platform.lib import Configuration, names, \
    BaseWithLog, info_function_start_finish, create_cert, ssl_questions
from os import path
from OpenSSL import crypto
from shutil import copy2


class EnableWebSsl(BaseWithLog):
    """
    Creates or enables existing certificates on Swimlane web.
    """

    def __init__(self, config):
        # type: (Configuration) -> EnableWebSsl
        super(EnableWebSsl, self).__init__(config)
        self.install_dir = names.INSTALL_DIR
        self.env_root = path.join(self.install_dir, names.SECRETS_SUB_FOLDER)
        self.secrets = path.join(self.install_dir, names.SECRETS_SUB_FOLDER)

    @info_function_start_finish('Enable SSL for Web')
    def run(self):
        # type: () -> None
        """
        Runs modifications to environment to enable additional settings for SSL
        """
        if self.config.args.web_ssl_self_signed:
            self.generate_certificates()
        else:
            # verify about names
            copy2(self.config.args.web_ssl_certificate, path.join(self.secrets, names.SSL_WEB_CERTIFICATE))
            copy2(self.config.args.web_ssl_key, path.join(self.secrets, names.SSL_WEB_KEY))

    def generate_certificates(self):
        # type: () -> None
        """
        Generates and saves web certificates
        """
        self.config.collect(ssl_questions)
        c, k = create_cert(country=self.config.args.ssl_country,
                           state=self.config.args.ssl_state,
                           location=self.config.args.ssl_location,
                           company=self.config.args.ssl_company,
                           application=self.config.args.ssl_application,
                           dns=self.config.args.ssl_dns)
        with open(path.join(self.secrets, names.SSL_WEB_KEY), "wb") as fw:
            fw.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
        with open(path.join(self.secrets, names.SSL_WEB_CERTIFICATE), "wb") as fw:
            fw.write(crypto.dump_certificate(crypto.FILETYPE_PEM, c))


def run(config):
    # type: (Configuration) -> None
    """
    The script run method, that can be called by other script or from file run method.
    :param config: Configuration information collected by parent script.
    """
    EnableWebSsl(config).run()
