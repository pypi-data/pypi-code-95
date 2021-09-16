import argparse
from bertdotbill.defaults import app_name

from bertdotbill.defaults import webengine_choices

def parse_args(**kwargs):

  parser = argparse.ArgumentParser(description=app_name)
  parser.add_argument('--username', '-u', help="Username, if the URL requires authentication")
  parser.add_argument('--password', '-p', help="Password, if the URL requires authentication")
  parser.add_argument('--lesson-url', '-url', help="The URL for the lesson definition")
  parser.add_argument('--webengine', '-g', choices=webengine_choices, help="The Web Renderer")
  parser.add_argument('--window-width', '-W', default=1024, type=int, help="App Window Width")
  parser.add_argument('--window-height', '-H', default=600, type=int, help="App Window Height")
  parser.add_argument('--config-file', '-f', help="Path to app configuration file")
  parser.add_argument('--config-file-templatized', '-fT', action='store_true', default=True, help="Render configuration via jinja2 templating")
  parser.add_argument('--no-ui', '-noui', action='store_true', help="Don't launch the UI")
  parser.add_argument('--no-init', '-noinit', action='store_true', help="Skip all UI init steps")
  parser.add_argument('--no-init-lesson', '-noinitl', action='store_true', help="Skip UI init Lesson steps")
  parser.add_argument('--debug', action='store_true')
  parser.add_argument('--verify-tls', action='store_true', help='Verify SSL cert when downloading web content', default=False)
  parser.add_argument('--norender-markdown', '-nomarkdown', action='store_true')
  return parser.parse_args()