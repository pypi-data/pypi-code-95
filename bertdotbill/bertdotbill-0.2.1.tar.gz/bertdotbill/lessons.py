import base64
from bertdotbill.defaults import default_terminal_address
from bertdotbill.logger import Logger
from bertdotbill.config import SuperDuperConfig
import sys

logger = Logger().init_logger(__name__)

class Lessons():

  def __init__(self, **kwargs):
    self.settings = kwargs['settings']
    self.args = kwargs['args']
    self.superconf = SuperDuperConfig(verify_tls=self.args.verify_tls)

  def initialize(self, webview):
    if len(webview.windows) > 0:
      logger.info('Initializing Lesson View')
      default_console_address = self.superconf.get(
        self.settings,'terminals.default.address', default_terminal_address
      )
      terminals = self.settings.get('terminals', {})
      if terminals:
        terminal_address = terminals.get(
          'footer',{}).get('address', default_console_address)
      else:
        terminal_address = default_console_address
      webview.windows[0].evaluate_js('window.pywebview.state.setiFrameURL("%s")' % terminal_address)
      if not self.args.no_init:
        webview.windows[0].evaluate_js('window.pywebview.state.loadLesson("")')
        if not self.args.no_init_lesson:
          webview.windows[0].evaluate_js('window.pywebview.state.setLessons("%s")' % self.load())
    else:
      logger.info('Skipped Lesson View Initialization')

  def load(self):

    logger.info('Loading available topics')
    topics = self.settings.get('topics', {})
    lessons_html = ''
    available_lesson_count = 0
    if isinstance(topics, dict):
      lessons_html = '<a href="#">Available Lessons</a>\n'
      lessons_html += "<ul class='nav first'>"
      for lesson_name, lesson_data in topics.items():
        lessons_html += '<li>%s\n' % lesson_name
        if isinstance(lesson_data, dict):
          lessons = lesson_data.get('lessons', [])
          lessons_html += '<ul class="nav">\n'
          if isinstance(lessons, list):
            for lesson in lessons:
              if isinstance(lesson, dict):
                topic_name = lesson.get('name','')
                topic_url = lesson.get('url','#')
                lessons_html += '<li><button onclick="window.pywebview.api.load_lesson(\'%s\')">%s</button></li>\n' % (topic_url, topic_name)
            lessons_html += '</ul>\n</li>'
    if sys.version_info[0] >= 3:
        b64_lessons = base64.standard_b64encode((lessons_html).encode()).decode()
    else:
        b64_lessons = base64.standard_b64encode(lessons_html)
    logger.info('Successfully loaded available lessons')
    return b64_lessons