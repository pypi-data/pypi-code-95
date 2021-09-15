from bertdotbill.defaults import app_name
from bertdotbill.api import API
from bertdotbill.entrypoint import get_entrypoint
from bertdotbill.ui import UI
from bertdotbill.cli import parse_args
from bertdotbill.config import read_config
from bertdotbill.logger import Logger
import sys
import webview

# Read command-line args
args = parse_args()
# Initialize logging facility
logger = Logger().init_logger(__name__)
# Initialize Config Reader
superconf, settings = read_config(
  args=args, verify_tls=args.verify_tls
  )
# Initialize UI
ui = UI(settings=settings, args=args)
# Get html entrypoint
entry = get_entrypoint()

def main():

  # Load UI
  if not args.no_ui:
    logger.info('UI entrypoint is %s' % entry)
    window = webview.create_window(
      app_name,
      entry,
      js_api=API(webview, superconf, args, settings),
      width=args.window_width,
      height=args.window_height,      
      text_select=True)
    # Start the webview object, with initial function lessons.initialize
    # being called, with args webview,
    webview.start(ui.initialize, args=[webview], gui=args.webengine, debug=args.debug)
  else:
    # Run via console only
    lesson_url = args.lesson_url
    if not lesson_url:
      logger.error('When operating in noui mode, ensure you specify a lesson url')
      sys.exit(1)
    js_api=API(webview, superconf, args, settings)
    js_api.load_lesson(lesson_url, no_ui=True, norender_markdown=args.norender_markdown)

if __name__ == '__main__':
  main()