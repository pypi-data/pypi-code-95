"""
Base settings for Django app.
"""

SITE_ID = 1

INTERNAL_IPS = ['127.0.0.1']

META_USE_SITES = True
META_SITE_PROTOCOL = 'https'

INSTALLED_APPS = [
    # This app. :-)
    # It is holding at the top of the list, so that allow rewrite the templates in third side applications.
    'cms_qe',
    'cms_qe_auth',
    'cms_qe_breadcrumb',
    'cms_qe_i18n',
    'cms_qe_menu',
    'cms_qe_newsletter',
    'cms_qe_table',
    'cms_qe_video',
    'cms_qe_analytical',

    # Must be before django.contrib.admin.
    'djangocms_admin_style',

    # Django's defaults.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Needed by Django CMS.
    'django.contrib.sitemaps',

    # Django CMS's core modules.
    'cms',
    'menus',
    'treebeard',  # Tree structure of pages and plugins.
    'sekizai',  # Static file management.

    # Other Django CMS's useful modules.
    'djangocms_text_ckeditor',
    'djangocms_googlemap',
    'aldryn_boilerplates',
    'aldryn_forms',
    'aldryn_forms.contrib.email_notifications',
    'captcha',  # Needed by Aldryn Forms.

    # Django Filer's modules.
    'filer',
    'easy_thumbnails',
    'mptt',

    # Other Django Files's useful modules.
    'djangocms_file',

    # Django CMS Bootstrap 4 from https://github.com/divio/djangocms-bootstrap4
    'djangocms_icon',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_bootstrap4',
    'djangocms_bootstrap4.contrib.bootstrap4_alerts',
    'djangocms_bootstrap4.contrib.bootstrap4_badge',
    'djangocms_bootstrap4.contrib.bootstrap4_card',
    'djangocms_bootstrap4.contrib.bootstrap4_carousel',
    'djangocms_bootstrap4.contrib.bootstrap4_collapse',
    'djangocms_bootstrap4.contrib.bootstrap4_content',
    'djangocms_bootstrap4.contrib.bootstrap4_grid',
    'djangocms_bootstrap4.contrib.bootstrap4_jumbotron',
    'djangocms_bootstrap4.contrib.bootstrap4_link',
    'djangocms_bootstrap4.contrib.bootstrap4_listgroup',
    'djangocms_bootstrap4.contrib.bootstrap4_media',
    'djangocms_bootstrap4.contrib.bootstrap4_picture',
    'djangocms_bootstrap4.contrib.bootstrap4_tabs',
    'djangocms_bootstrap4.contrib.bootstrap4_utilities',

    # Other Django's modules.
    'axes',
    'bootstrapform',
    'constance',
    'constance.backends.database',
    'import_export',
    'mailqueue',
]

MIDDLEWARE = [
    # Must be the first. Cache is more important, second one is only
    # for development auto-reload also after apphook changes.
    'django.middleware.cache.UpdateCacheMiddleware',
    'cms.middleware.utils.ApphookReloadMiddleware',

    # Django's defaults.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Locale is mandatory by Django CMS.
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Extra Django's middlewares.
    'django.middleware.common.BrokenLinkEmailsMiddleware',

    # Django CMS's core middlewares.
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',

    # Security middleware.
    'csp.middleware.CSPMiddleware',

    # Must be the last.
    'django.middleware.cache.FetchFromCacheMiddleware',
]
