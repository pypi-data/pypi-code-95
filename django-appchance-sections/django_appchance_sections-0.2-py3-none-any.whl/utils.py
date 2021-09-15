import importlib
from typing import Type

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from appchance_sections.conf import SECTION_CONTENT_MODEL, SECTION_MODEL
from appchance_sections.models import DynamicContentAbstract


def get_section_model():
    """
    Return the Section model that is active in this project.
    """
    try:
        return django_apps.get_model(SECTION_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("SECTION_MODEL must be of the form 'app_label.model_name'") from None
    except LookupError:
        raise ImproperlyConfigured(
            "SECTION_MODEL refers to model '%s' that has not been installed" % SECTION_MODEL
        ) from None
    except AttributeError:
        raise ImproperlyConfigured("SECTION_MODEL must be defined in settings.") from None


Section = get_section_model()


def get_content_model():
    """
    Return the Content model that is active in this project.
    """

    try:
        parts = SECTION_CONTENT_MODEL.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError:
        raise ImproperlyConfigured("SECTION_CONTENT_MODEL must be of the form 'app_label.path.model_name'") from None


Content = get_content_model()


def register_section_content(
    slug, name, url, *, query_params=None, path_params=None, widgets=None, placements=None, prefix=None
):
    SectionRegistry.register_content(
        slug=slug,
        name=name,
        url=url,
        query_params=query_params,
        path_params=path_params,
        widgets=widgets,
        placements=placements,
        prefix=prefix,
    )


def register_dynamic_content(content_class: Type[DynamicContentAbstract]):
    SectionRegistry.register_dynamic_content(content_class=content_class)


def register_content_callback(callback):
    SectionRegistry.register_content_callback(callback)


def unregister_contents():
    SectionRegistry.unregister_contents()


def unregister_dynamic_contents():
    SectionRegistry.unregister_dynamic_contents()


class SectionRegistry:
    _contents = Section._contents  # pylint: disable=W0212
    _content_callbacks = Section._content_callbacks  # pylint: disable=W0212

    @classmethod
    def register_content(
        cls, slug, name, url, *, query_params=None, path_params=None, widgets=None, placements=None, prefix=None
    ):
        content = Content(
            slug=slug,
            name=name,
            url=url,
            query_params=query_params,
            path_params=path_params,
            widgets=widgets,
            placements=placements,
            prefix=prefix,
        )
        cls._contents[content.slug] = content

    @classmethod
    def register_dynamic_content(cls, content_class: Type[DynamicContentAbstract]):
        def _callback():
            contents = content_class.get_all_objects()
            items = []
            for content in contents:
                query_params = content_class.QUERY_PARAMS or {}
                if content_class.FILTER_ATTRIBUTE:
                    query_params[content_class.FILTER_ATTRIBUTE] = content.id
                path_params = None if content_class.FILTER_ATTRIBUTE else {"pk": content.id}

                items.append(
                    Content(
                        slug=content.content_slug,
                        name=content.name_field,
                        url=content_class.URL,
                        query_params=query_params,
                        path_params=path_params,
                        widgets=content_class.WIDGETS,
                        placements=content_class.PLACEMENTS,
                        prefix=(content_class.PREFIX or content_class.__name__),
                    )
                )
            return items

        cls.register_content_callback(callback=_callback)

    @classmethod
    def register_content_callback(cls, callback):
        cls._content_callbacks.add(callback)

    @classmethod
    def unregister_contents(cls):
        cls._contents.clear()

    @classmethod
    def unregister_dynamic_contents(cls):
        cls._content_callbacks.clear()
