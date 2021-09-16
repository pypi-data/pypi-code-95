import importlib
import asyncio
import traceback
import signal
import sys

from django.core.management import BaseCommand
from django.conf import settings

from servitin.log import configure_logging, log
from servitin import __version__ as servitin_version


loop = asyncio.get_event_loop()


class Command(BaseCommand):
    SERVICES = []
    help = 'Run servitin services 🌐'

    def add_arguments(self, parser):
        # "--name" argument
        parser.add_argument(
            "-n",
            '--name',
            dest='service_name',
            help='service name to run, this is app name form settings.INSTALLED_APPS',
            type=str
        )

    def start(self, loop, cmd_service_name):
        """
        start services
        :param loop: asyncio.loop
        :param cmd_service_name: service name to run
        """

        # import servitin settings for populate django settings with default values
        importlib.import_module('servitin.settings')

        # save all found services data in self.SERVICES
        self.get_service_apps()

        configure_logging(self.SERVICES)

        # cmd_service_name = cmd: "--name=example_service"
        if cmd_service_name:
            self.SERVICES = [s for s in self.SERVICES if s['app_name'] == cmd_service_name]
            if not len(self.SERVICES):
                raise Exception(f"Specified service '{cmd_service_name}' not found. Check settings.INSTALLED_APPS")

        for s in self.SERVICES:
            log(s['logger'], 'info', 'servitin', f"v{servitin_version}, start: {s['app_name']} v{s['version']}")

            # start service
            service_instance = s['class'](
                loop,
                s["app_name"],
                s['version'],
                s['logger'],
                s['log'],
            )
            s['instance'] = service_instance

    def stop(self):
        """
        stop services
        """

        for s in self.SERVICES:
            if s.get('instance', None):
                log(s['logger'], 'info', 'servitin', f"stop: {s['app_name']} v{s['version']}")

                # stop service
                try:
                    s['instance'].stop()
                except Exception as e:
                    log(s['logger'], 'critical', s['instance'].app_name, f'Stop error: {e.__repr__()}')
                finally:
                    # cancel all pending asyncio tasks
                    for task in asyncio.all_tasks(loop):
                        task.cancel()

    def signal_sigterm_handler(self, sig, frame):
        for s in self.SERVICES:
            log(s['logger'], 'info', 'servitin', "SIGTERM signal received")
        sys.exit(777)

    def get_service_apps(self):
        """
        get services apps
        """

        for app_name in settings.INSTALLED_APPS:
            try:
                apps_module = importlib.import_module(f'{app_name}.apps')
            except Exception:
                continue

            for item in dir(apps_module):
                app_config = getattr(apps_module, item)
                if isinstance(app_config, type):  # is class?
                    if 'AppConfig' in [x.__name__ for x in app_config.__bases__]:  # is based on AppConfig?
                        if getattr(app_config, 'is_servitin', False):  # is servitin service?
                            # import modules
                            service_module = importlib.import_module(app_name)
                            service_servitin_module = importlib.import_module(f'{app_name}.servitin')
                            # import service settings for populate django settings with default values
                            importlib.import_module(f'{app_name}.settings')

                            self.SERVICES.append({
                                'app_config': app_config,
                                'app_name': app_name,
                                'version': getattr(service_module, '__version__', 'UNDEFINED'),
                                'class': getattr(service_servitin_module, 'Service'),
                            })

    def handle(self, *args, **options):
        service_name = options['service_name']  # cmdline arg: what service to run?

        signal.signal(signal.SIGTERM, self.signal_sigterm_handler)

        try:
            self.start(loop, service_name)
            loop.run_forever()

        except asyncio.CancelledError as e:
            for s in self.SERVICES:
                log(s['logger'], 'critical', 'servitin', e.__repr__(), traceback=traceback.format_exc())

        except (KeyboardInterrupt, SystemExit) as e:
            for s in self.SERVICES:
                log(s['logger'], 'info', 'servitin', e.__repr__())

        except Exception as e:
            for s in self.SERVICES:
                log(s['logger'], 'critical', 'servitin', e.__repr__(), traceback=traceback.format_exc())
            raise e

        finally:
            self.stop()
            loop.close()
