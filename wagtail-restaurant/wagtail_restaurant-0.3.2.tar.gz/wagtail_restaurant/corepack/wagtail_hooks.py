from wagtail.core import hooks


# Hide reports menu from admin
@hooks.register('construct_main_menu')
def hide_reports_menu_item(request, menu_items):
  menu_items[:] = [item for item in menu_items if item.name != 'reports']

# On save page default action make "publish"
@hooks.register('construct_page_action_menu')
def make_publish_default_action(menu_items, request, context):
  for (index, item) in enumerate(menu_items):
    if item.name == 'action-publish':
      menu_items.pop(index)
      menu_items.insert(0, item)
      break



# External link target
from django.utils.html import escape
from wagtail.core.rich_text import LinkHandler

class NewWindowExternalLinkHandler(LinkHandler):
    # This specifies to do this override for external links only.
    identifier = 'external'

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        return '<a href="%s" target="_blank" rel="noopener noreferrer">' % escape(href)

@hooks.register('register_rich_text_features')
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)



