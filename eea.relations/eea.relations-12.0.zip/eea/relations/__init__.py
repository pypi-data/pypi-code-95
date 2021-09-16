""" EEA Relations
"""
has_archetypes = True
try:
    from Products.Archetypes.ReferenceEngine import ReferenceCatalog
    from Products.Archetypes.Referenceable import Referenceable
    from patches.patch_archetypes_referenceable import \
        patched_optimizedGetObject
    from patches.patch_archetypes_reference_engine import \
        patched_uidFor
except ImportError:
    has_archetypes = False

if has_archetypes:
    ReferenceCatalog._uidFor = patched_uidFor
    Referenceable._optimizedGetObject = patched_optimizedGetObject

def initialize(context):
    """ Zope 2 """
    from eea.relations import validators
    validators.register()

    from eea.relations import field
    field.register()

    from eea.relations import widget
    widget.register()

    from eea.relations import content
    content.initialize(context)
