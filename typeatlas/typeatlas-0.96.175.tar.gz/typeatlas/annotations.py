# -*- coding: utf-8 -*-
#
#    TypeAtlas Font Annotations
#    Copyright (C) 2018-2021 Milko Krachounov
#
#    This file is part of TypeAtlas
#
#    TypeAtlas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    TypeAtlas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TypeAtlas.  If not, see <http://www.gnu.org/licenses/>.
#
#                                 ***
#
#    Alternatively, you may use this file (part of TypeAtlas libraries)
#    under the terms of the X11/MIT license as follows:
#
#    Permission is hereby granted, free of charge, to any person
#    obtaining a copy of this software and associated documentation
#    files (the "Software"), to deal in the Software without
#    restriction, including without limitation the rights to use,
#    copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following
#    conditions:
#
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#    OTHER DEALINGS IN THE SOFTWARE.
#

"""Annotations carry information about terms, objects and entities that can
be displayed to the user."""

from typeatlas.util import N_, generic_type
from collections.abc import Iterable, Callable

IterableOf = generic_type('Iterable')
IteratorOf = generic_type('Iterator')
TupleOf = generic_type('Tuple')


# TODO: Annotate color fonts. Details about use, e.g. PCF/BDF.
# Annotate extensions and mime types, unicode support, OS/browser support.
# Annotate purpose, annotate non-standard, annotate comments (X11 font?)
# native platform, etc.
# Annotate Adobe SVG viewer in CEF_FILE


PROPER_NAME = 1 << 0
COMMON_NAME = 1 << 1

PREFERRED_NAME = 1 << 2
OFFICIAL_NAME = 1 << 3

STANDARD_NAME_BIT = 1 << 4
STANDARD_NAME = OFFICIAL_NAME | STANDARD_NAME_BIT

PROPRIETARY_NAME_BIT = 1 << 5
PROPRIETARY_NAME = OFFICIAL_NAME | PROPRIETARY_NAME_BIT

TRADEMARK_BIT = 1 << 6
TRADEMARK = PROPER_NAME | PROPRIETARY_NAME | TRADEMARK_BIT

REGISTERED_BIT = 1 << 7
REGISTERED = TRADEMARK | REGISTERED_BIT

UNOFFICIAL_NAME = 1 << 8
GENERIC_NAME = 1 << 9
ALT_NAME = 1 << 10

FULL_NAME = 1 << 11
LEGAL_NAME_BIT = 1 << 12
LEGAL_NAME = FULL_NAME | LEGAL_NAME_BIT
ABBREVIATION = 1 << 13


FORMAT_GENERIC_CATEGORY = 1 << 0
FORMAT_SPECIFIC_CATEGORY = 1 << 1
FORMAT_INSTANCE = 1 << 2

FILE_FORMAT = 1 << 3
DATA_FORMAT = 1 << 4


SPEC_STANDARD = 0
SPEC_RECOMMENDATION = 1 
SPEC_DRAFT = 3

BINDING_DEFAULT = object()
BINDING_LIKELY = object()


display_names = [
    (N_('Alternative name'), ALT_NAME),
    (N_('Standard name'), STANDARD_NAME),
    (N_('Name'), TRADEMARK),
    (N_('Name'), PROPRIETARY_NAME),
    (N_('Name'), OFFICIAL_NAME),
    (N_('Unofficial name'), UNOFFICIAL_NAME),
    (N_('Name'), PROPER_NAME),
    (N_('Name'), COMMON_NAME),
]


class Name(object):

    """Describe one of the names of an entity.

    The flags describe what type of name is that, e.g. TRADERMARK would identify
    this as a trademark (which can be checked with flags & TRADEMARK_BIT), and
    ABBREVIATION would be an abbreviation.

    The entities are a list of Annotation objects describing entities (organizations)
    that pertain to the name, e.g. they are the trademark owner.

    The type_label can be a translatable string that displays a human-readable
    representation of the type of name, especially if it can't be represented
    with the flags. E.g. N_('Metonym').

    The trademarked argument refers to which subset of the name is trademarked.
    """

    def __init__(self, text: str, flags: int=0,
                       entities: 'IterableOf[EntityAnnotation]'=None,
                       type_label: str=None,
                       trademarked: str=None):
        self.text = text
        self.flags = flags
        self.entities = list(entities or ())
        self.type_label = type_label
        self.trademarked = trademarked

    def decorated_text(self) -> str:
        """Return a version of the name with e.g. a trademark symbol"""
        if not (self.flags & TRADEMARK_BIT):
            return self.text
        sym = '®' if (self.flags & REGISTERED_BIT) else '™'
        if self.trademarked and self.trademarked in self.text:
            return self.text.replace(self.trademarked, 
                                     self.trademarked + sym, 1)
        return self.text + sym

    def __str__(self):
        return self.decorated_text()

    def __repr__(self):
        return "<%s %r at %x>" % (type(self).__name__,
                                  self.text, id(self))


def short(name) -> object:
    """A key function that sorts short names before long names,
    used e.g. for the prefer argument of get_name()"""
    return name.flags & ABBREVIATION, not (name.flags & FULL_NAME)


def long(name) -> object:
    """A key function that sorts long names before short names,
    used e.g. for the prefer argument of get_name()"""
    return name.flags & FULL_NAME, not (name.flags & ABBREVIATION)


class Annotation(object):

    """Annotation of a given term, object, or entity. This is the base class.

    It can have multiple names, an icon, flags describing the category of the
    objects, such as FILE_FORMAT to describe file formats, FORMAT_GENERIC_CATEGORY
    to describe a category of formats, and FORMAT_INSTANCE to describe
    the exact instance of a format. Some are filled by subclasses.

    It can have generic entities (organizations) pertaining to the subject
    of the annotation, and more specific entities such as developers,
    standard_entities (e.g. standard organization that approved this
    format as a standard), as well as standard_reference (ID),
    standard_level (SPEC_DRAFT, SPEC_RECOMMENDATION or SPEC_STANDARD),
    and an applicable illustration.

    The parents argument provides a list of annotations describing what
    the annotated thing is a subset of. For example, Type 1 font
    format is a type of an online font.

    The extends argument provides an annotation describing what
    the annotated thing is an extended version of. For example,
    OpenType file format is extended from the TrueType file format.
    """

    binding = BINDING_DEFAULT

    def __init__(self, names: IterableOf[str], *args,
                       icon: str=None, flags: int=0,
                       parents: 'IterableOf[Annotation]'=None,
                       properties: Iterable=None,
                       entities: 'IterableOf[EntityAnnotation]'=None,
                       developers: 'IterableOf[EntityAnnotation]'=None,
                       standard_entities: 'IterableOf[EntityAnnotation]'=None,
                       standard_reference: str=None,
                       standard_level: int=SPEC_STANDARD,
                       illustration: str=None,
                       extends: 'Annotation'=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.names = list(names)
        self.icon = icon
        self.flags = flags
        self.parents = list(parents or ())
        self.properties = list(properties or ())
        self.entities = list(entities or ())
        self.developers = list(developers or ())
        self.standard_entities = list(standard_entities or ())
        self.standard_reference = standard_reference
        self.standard_level = standard_level
        self.extends = extends
        self.illustration = illustration

        self.other_entities = list(self.entities)
        self.entities.extend(self.developers)
        if self.standard_entities:
            self.entities.extend(self.standard_entities)

    def __repr__(self):
        return "<%s %r at %x>" % (type(self).__name__,
                                  self.names[:1], id(self))

    @property
    def parent(self) -> 'Annotation':
        """The annotation of the first parent entity, object, or term. For example,
        TrueType font format is a type of an outline font, so its parent
        might be OUTLINE_FONT."""
        if not self.parents:
            return None
        return self.parents[0]

    def relations(self, translate: Callable=N_,
                        extended: bool=True, categories: bool=False,
                        parents: bool=True, deep: bool=True,
                        include_self: bool=True) -> 'IterableOf[tuple[str, Annotation]]':
        """Yield relations of the annotated thing with other annotated
        things, such as what it was extended from, and what it is a variant
        (child) of. Each yielded value is a tuple of an optionally translated
        string (or None) and an Annotation object describing the object of the
        relation.

        Use this to display more information about the annotation to
        the user.

        You can select which relations to include. This is recursive,
        unless deep=False is passed.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.
        """

        _ = translate

        if include_self:
            yield None, self

        if self.extends and extended:
            yield _('Extended from'), self.extends
            if deep:
                yield from self.extends.relations(translate, parents=False,
                                                  include_self=False)

        category = getattr(self, 'category', None)

        if self.parents and parents:
            for parent in self.parents:
                if parent is category and not categories:
                    continue

                yield _('A variant of'), parent
                if deep:
                    yield from parent.relations(translate, extended=False,
                                                include_self=False)

    def annotations(self) -> 'IterableOf[Annotation]':
        """Yield all annotations, including this one and its parents."""
        yield self
        for parent in self.parents:
            yield from parent.annotations()

    def ancestors(self) -> 'IterableOf[Annotation]':
        """Yield all ancestor, including the parents and their parents."""
        for parent in self.parents:
            yield parent
            yield from parent.ancestors()

    def get_name_tuples(self, prefer=PREFERRED_NAME,
                              translate: Callable=N_,
                              decorated: bool=False) -> TupleOf[str, str, Name]:
        """Yield tuples with (optionally translated) header - such as Official
        name, (optionally translated) name string, and name object.

        The returned names are ordered by the provided reference, which can
        be a flag  or a callable that receives the name object as an argument.
        One can use annotations.short or annotations.long functions here.

        If decorated=True is passed, trademark symbols may be added.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.
        """

        if not callable(prefer):
            prefer = lambda name, prefer=prefer: name.flags & prefer

        names = sorted(self.names, key=prefer, reverse=True)

        shown = 0

        for name in self.names:
            for header, flags in display_names:
                if (flags & name.flags) == flags and (shown & flags) != flags:
                    if decorated:
                        text = name.decorated_text()
                    else:
                        text = name.text
                    yield translate(header), translate(text), name
                    shown |= name.flags
                    break

    def get_name_object(self, prefer=PREFERRED_NAME) -> Name:
        """Return the best name object for the annotated thing.

        The names are ordered by the provided reference, which can
        be a flag  or a callable that receives the name object as an argument.
        One can use annotations.short or annotations.long functions here.
        """

        if not callable(prefer):
            prefer = lambda name, prefer=prefer: name.flags & prefer

        names = sorted(self.names, key=prefer, reverse=True)

        for name in names:
            return name
        return None

    def get_name(self, prefer=PREFERRED_NAME,
                       translate: Callable=N_,
                       decorated: bool=False) -> str:
        """Return the best name string for the annotated thing, optionally
        translated.

        The names are ordered by the provided reference, which can
        be a flag  or a callable that receives the name object as an argument.
        One can use annotations.short or annotations.long functions here.

        If decorated=True is passed, trademark symbols may be added.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.
        """

        name = self.get_name_object(prefer)
        if name is not None:
            if decorated:
                text = name.decorated_text()
            else:
                text = name.text
            return translate(text)
        return ''

    def get_header(self, translate: Callable=N_) -> str:
        """Return an optionally-translated string describing what the annotated
        thing is (as row/column header), such as file format, font format, etc.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.
        """
        _ = translate
        if self.flags & FORMAT_INSTANCE:
            if self.flags & DATA_FORMAT:
                return _('Font format')
            elif self.flags & FILE_FORMAT:
                return _('File format')

        if self.flags & FORMAT_SPECIFIC_CATEGORY:
            return _('Type')
        if self.flags & FORMAT_GENERIC_CATEGORY:
            return _('Category')

        # Display something useful as fallback
        return type(self).__name__

    def get_notes(self, translate: Callable=N_,
                        trademarks: bool=False) -> IteratorOf[str]:
        """Yield optionally-translated notes describes who developed
        this, who standardized it, what type of standard it is.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.

        If trademarks=True is passed, trademarks are included too.
        """
        _ = translate
        for developer in self.developers:
            yield _('Developed by %s') % (developer.get_name(), )

        if self.standard_reference:
            standard = self.standard_reference
        elif self.standard_entities:
            standard = '/'.join(entity.get_name() 
                                 for entity in self.standard_entities)
        else:
            standard = None

        if standard:
            if self.standard_level == SPEC_DRAFT:
                standard_label = _('Draft')
            elif self.standard_level == SPEC_RECOMMENDATION:
                standard_label = _('Recommendation')
            elif self.standard_level == SPEC_STANDARD:
                standard_label = _('noun|Standard')
            yield '%s; %s' % (standard_label, standard)
                                
        for other_entity in self.other_entities:
            yield _('Related entity: %s') % (other_entity.get_name(), )

        if trademarks:
            yield from self.get_trademarks(translate)

    def get_trademarks(self, translate: Callable=N_,
                             recursive: bool=True) -> IteratorOf[str]:
        """Yield trademarks strings.

        You can provide a translation function with translate=_. One
        should pass translate, as the returned value is not guaranteed
        to be translatable as-is.

        If recursive=True is passed, the trademarks are returned
        recursively.
        """
        _ = translate

        seen = set()

        for name in self.names:
            if not (name.flags & TRADEMARK_BIT):
                continue

            mark = name.text 
            if name.trademarked:
                mark = name.trademarked

            if mark in seen:
                continue

            seen.add(mark)

            if name.entities:
                owner = name.entities[0]
            else:
                owner = self

            if name.flags & REGISTERED_BIT:
                template = _('{name} is a registered trademark of {owner}')
            else:
                template = _('{name} is a trademark of {owner}')

            yield template.format(name=mark, 
                                  owner=owner.get_name(translate=translate, 
                                                       decorated=False))

        if recursive:
            for entity in self.entities:
                yield from entity.get_trademarks(translate, recursive)


class AnnotationWrap(object):

    """Wrap another annotation for some purpose, to provide additional
    decoration of it."""

    def __init__(self, wrapped: Annotation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wrapped = wrapped

    def __getattr__(self, attr):
        return getattr(self.wrapped, attr)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self.wrapped)

    @property
    def wrapper_object_for(self):
        """Provide the real object to our type checker."""
        return self.wrapped


class Likely(AnnotationWrap):

    """Likely version of an annotation. This changes the binding of
    the wrapped annotation to BINDING_LIKELY. When used in a relation,
    this means that we are not sure the relation exists, only suspect
    it."""

    binding = BINDING_LIKELY


class EntityAnnotation(Annotation):
    """Anotation for entities such as organizations."""
    pass


class FormatAnnotation(Annotation):
    """Anotation for formats."""
    pass


class FileFormatAnnotation(FormatAnnotation):
    """Anotation for file formats. Respective flags are added automatically.

    This differs from a font format. The file is the container, the font is
    the data, the two can have different formats."""

    def __init__(self, *args,
                       flags: int=0,
                       font_formats: 'IterableOf[FontFormatAnnotation]'=None,
                       **kwargs):

        flags |= FILE_FORMAT

        super().__init__(*args, flags=flags, **kwargs)
        self.font_formats = list(font_formats or ())
        for font_format in self.font_formats:
            font_format.file_formats.append(self)


class FontCategoryAnnotation(FormatAnnotation):
    """Anotation for font category. Respective flags are added automatically."""

    def __init__(self, *args,
                        scalable: bool=True,
                        parametric: bool=False, flags: int=0,
                        parents: IterableOf[Annotation]=None,
                       **kwargs):

        if not (flags & (FORMAT_SPECIFIC_CATEGORY | FORMAT_GENERIC_CATEGORY)):
            if parents:
                flags |= FORMAT_SPECIFIC_CATEGORY
            else:
                flags |= FORMAT_GENERIC_CATEGORY
        flags |= DATA_FORMAT

        super().__init__(*args, flags=flags, parents=parents, **kwargs)
        self.scalable = scalable
        self.parametric = parametric


class FontFormatAnnotation(FormatAnnotation):
    """Anotation for font format. Respective flags are added automatically.

    This differs from a file format. The file is the container, the font is
    the data, the two can have different formats."""

    def __init__(self, *args,
                       category: FontCategoryAnnotation,
                       file_formats: IterableOf[FileFormatAnnotation]=None,
                       flags: int=0,
                       parents: IterableOf[Annotation]=None, **kwargs):

        flags |= DATA_FORMAT | FORMAT_INSTANCE

        parents = list(parents or ())
        parents.append(category)

        super().__init__(*args, flags=flags, parents=parents, **kwargs)
        self.category = category
        self.file_formats = list(file_formats or ())
        for file_format in self.file_formats:
            file_format.font_formats.append(self)

    def categories(self):
        return self.category.annotations()


def make_pair(*args, category: FontCategoryAnnotation,
              **kwargs) -> TupleOf[FileFormatAnnotation, FontFormatAnnotation]:
    """Create both file and font format for a thing where the two are one and
    the same. Arguments are the same as for FontFormatAnnotation."""
    file_format = FileFormatAnnotation(*args, **kwargs)
    font_format = FontFormatAnnotation(*args, category=category, **kwargs)
    file_format.font_formats.append(font_format)
    font_format.file_formats.append(file_format)
    return file_format, font_format



BITMAP_FONT = FontCategoryAnnotation([
                    Name(N_('Bitmap'), COMMON_NAME | PREFERRED_NAME),
                    Name(N_('Raster'), COMMON_NAME),
                ], icon='bitmap', illustration='bitmap-font-character.png')

OUTLINE_FONT = FontCategoryAnnotation([
                    Name(N_('Outline'), COMMON_NAME | PREFERRED_NAME),
                    Name(N_('Vector'), COMMON_NAME),
                ], icon='outline')

STROKE_FONT = FontCategoryAnnotation([
                    Name(N_('Stroke'), COMMON_NAME | PREFERRED_NAME),
                ])

CUBIC_BEZIER_FONT = FontCategoryAnnotation(
                [Name(N_('Cubic Bézier outline'), COMMON_NAME | PREFERRED_NAME)],
                parents=[OUTLINE_FONT], illustration='cubic-bezier.svgz')
QUADRATIC_BEZIER_FONT = FontCategoryAnnotation(
                [Name(N_('Quadratic Bézier outline'),
                  COMMON_NAME | PREFERRED_NAME)],
                parents=[OUTLINE_FONT], illustration='quadratic-bezier.svgz')


MICROSOFT = EntityAnnotation([
            Name('Microsoft', REGISTERED | PREFERRED_NAME),
            Name('Microsoft Corporation', REGISTERED | LEGAL_NAME,
                 trademarked='Microsoft'),
            Name('MS', PROPER_NAME | PROPRIETARY_NAME | ABBREVIATION),
            Name('Redmond', PROPER_NAME | GENERIC_NAME | UNOFFICIAL_NAME,
                 type_label=N_('Metonym')),
])

APPLE = EntityAnnotation([
            Name('Apple', REGISTERED | PREFERRED_NAME),
            Name('Apple Inc.', REGISTERED | LEGAL_NAME, trademarked='Apple'),
])


ADOBE = EntityAnnotation([
            Name('Adobe Systems', REGISTERED | PREFERRED_NAME,
                 trademarked='Adobe'),
            Name('Adobe Systems Incorporated', REGISTERED | LEGAL_NAME,
                 trademarked='Adobe'),
            Name('Adobe', REGISTERED | ABBREVIATION),
])


BITSTREAM = EntityAnnotation([
            Name('Bitstream', REGISTERED | PREFERRED_NAME),
            Name('Bitstream Inc.', REGISTERED | LEGAL_NAME,
                 trademarked='Bitstream'),
])



ISO = EntityAnnotation([
            Name('ISO', REGISTERED | ABBREVIATION | PREFERRED_NAME),
            Name(N_('International Organization for Standardization'),
                 PROPER_NAME | PROPRIETARY_NAME | FULL_NAME),
])

IEC = EntityAnnotation([
            Name('IEC', REGISTERED | ABBREVIATION | PREFERRED_NAME),
            Name(N_('International Electrotechnical Commission'),
                 PROPER_NAME | PROPRIETARY_NAME | FULL_NAME),
])


W3C = EntityAnnotation([
            Name('W3C', REGISTERED | ABBREVIATION | PREFERRED_NAME),
            Name(N_('World Wide Web Consortium'), TRADEMARK | FULL_NAME),
])



TRUETYPE_FILE = FileFormatAnnotation(
                [Name('TrueType', REGISTERED | PREFERRED_NAME,
                      entities=[APPLE]),
                 Name('TTF', PROPER_NAME | ABBREVIATION)],
                icon='ttf',
                developers=[APPLE, MICROSOFT])

OPENTYPE_FILE = FileFormatAnnotation(
                [Name('OpenType', REGISTERED | PREFERRED_NAME,
                      entities=[MICROSOFT]),
                 Name('Open Font Format', PROPER_NAME | STANDARD_NAME,
                      entities=[ISO]),
                 Name('OTF', PROPER_NAME | ABBREVIATION)],
                icon='otf',
                developers=[MICROSOFT, ADOBE],
                standard_entities=[ISO, IEC],
                standard_reference='ISO/IEC 14496-22:2015',
                extends=TRUETYPE_FILE)

TRUETYPE_FILE.parents.append(OPENTYPE_FILE)


DFONT_FILE = FileFormatAnnotation(
                [Name('Datafork TrueType', REGISTERED | PREFERRED_NAME,
                      entities=[APPLE], trademarked='TrueType'),
                 Name('dfont', PROPER_NAME | ABBREVIATION)],
                icon='ttf',
                developers=[APPLE], extends=TRUETYPE_FILE)

WOFF_FILE = FileFormatAnnotation(
                [Name('Web Open Font Format',
                      PROPER_NAME | STANDARD_NAME | PREFERRED_NAME,
                      entities=[W3C]),
                 Name('WOFF', PROPER_NAME | ABBREVIATION)],
                 icon='woff', 
                 standard_entities=[W3C],
                 standard_level=SPEC_RECOMMENDATION,
                 extends=OPENTYPE_FILE)

EMBEDDED_OPENTYPE_FILE = FileFormatAnnotation(
                [Name('Embedded OpenType', REGISTERED | PREFERRED_NAME,
                      entities=[MICROSOFT], trademarked='OpenType')],
                 icon='otf',
                 developers=[MICROSOFT],
                 extends=OPENTYPE_FILE)

POSTSCRIPT_FONT_FILE = FileFormatAnnotation(
                [Name(N_('PostScript font file'),
                      REGISTERED | PREFERRED_NAME,
                      entities=[ADOBE], trademarked='PostScript')],
                icon='ps-old',
                developers=[ADOBE])

PFA_FILE = FileFormatAnnotation(
                [Name('Printer Font ASCII',
                      PROPER_NAME | OFFICIAL_NAME | PREFERRED_NAME,
                      entities=[ADOBE]),
                 Name('PFA', PROPER_NAME | ABBREVIATION)],
                icon='ps-old',
                developers=[ADOBE],
                parents=[POSTSCRIPT_FONT_FILE])

PFB_FILE = FileFormatAnnotation(
                [Name('Printer Font Binary',
                      PROPER_NAME | OFFICIAL_NAME | PREFERRED_NAME,
                      entities=[ADOBE]),
                 Name('PFB', PROPER_NAME | ABBREVIATION)],
                icon='ps-old',
                developers=[ADOBE],
                parents=[POSTSCRIPT_FONT_FILE])


CFF_FILE = FileFormatAnnotation(
                [Name('Compact Font Format',
                      PROPER_NAME | OFFICIAL_NAME | PREFERRED_NAME,
                      entities=[ADOBE]),
                 Name('CFF', PROPER_NAME | ABBREVIATION)],
                icon='ps-old',
                developers=[ADOBE],
                parents=[POSTSCRIPT_FONT_FILE])

CEF_FILE = FileFormatAnnotation(
                [Name('Compact Embedded Font',
                      PROPER_NAME | OFFICIAL_NAME | PREFERRED_NAME,
                      entities=[ADOBE]),
                 Name('CEF', PROPER_NAME | ABBREVIATION)],
                icon='ps-old',
                developers=[ADOBE],
                parents=[POSTSCRIPT_FONT_FILE])

TRUETYPE_FONT = FontFormatAnnotation(
                [Name('TrueType', REGISTERED | PREFERRED_NAME,
                      entities=[APPLE])],
                icon='ttf', developers=[APPLE, MICROSOFT],
                category=QUADRATIC_BEZIER_FONT,
                file_formats=[TRUETYPE_FILE, OPENTYPE_FILE, WOFF_FILE,
                              DFONT_FILE, EMBEDDED_OPENTYPE_FILE])

TYPE42_FONT = FontFormatAnnotation(
                [Name('Type 42', PROPER_NAME | OFFICIAL_NAME | PREFERRED_NAME,
                      entities=[ADOBE]),
                 Name('TrueType wrapper', REGISTERED | ALT_NAME |
                                          UNOFFICIAL_NAME,
                      entities=[APPLE], trademarked='TrueType')],
                icon='ttf', developers=[APPLE, MICROSOFT],
                category=QUADRATIC_BEZIER_FONT,
                parents=[TRUETYPE_FONT],
                file_formats=[PFA_FILE, PFB_FILE, POSTSCRIPT_FONT_FILE])


POSTSCRIPT_FONT = FontFormatAnnotation(
                [Name(N_('PostScript font'),
                      PROPER_NAME | REGISTERED | PREFERRED_NAME,
                      entities=[ADOBE], trademarked='PostScript')],
                icon='ps', developers=[ADOBE],
                category=CUBIC_BEZIER_FONT,
                file_formats=[PFA_FILE, PFB_FILE, POSTSCRIPT_FONT_FILE,
                              OPENTYPE_FILE, WOFF_FILE])

TYPE1_FONT = FontFormatAnnotation(
                [Name('Type 1', PROPER_NAME | OFFICIAL_NAME | PREFERRED_NAME,
                      entities=[ADOBE])],
                icon='type1', developers=[ADOBE],
                category=CUBIC_BEZIER_FONT,
                file_formats=[PFA_FILE, PFB_FILE, POSTSCRIPT_FONT_FILE],
                parents=[POSTSCRIPT_FONT])


CFF_FONT = FontFormatAnnotation(
                [Name('Compact Font Format', PROPER_NAME | STANDARD_NAME |
                                             PREFERRED_NAME,
                      entities=[ISO]),
                 Name('CFF', PROPER_NAME | STANDARD_NAME | ABBREVIATION,
                      entities=[ISO]),
                 Name('Type 2', PROPER_NAME | OFFICIAL_NAME | ALT_NAME,
                      entities=[ADOBE])],
                icon='type2', developers=[ADOBE],
                category=CUBIC_BEZIER_FONT,
                file_formats=[OPENTYPE_FILE, WOFF_FILE,
                              DFONT_FILE, EMBEDDED_OPENTYPE_FILE,
                              CFF_FILE, CEF_FILE],
                parents=[POSTSCRIPT_FONT])


SVG_FONT = FontFormatAnnotation(
                [Name(N_('SVG color outline'),
                      PROPER_NAME | STANDARD_NAME | PREFERRED_NAME,
                      entities=[W3C]),
                 Name(N_('Scalable Vector Graphics color outline'),
                      PROPER_NAME | STANDARD_NAME | FULL_NAME,
                      entities=[W3C])],
                icon='svg', #developers=[W3C],
                standard_entities=[W3C],
                category=CUBIC_BEZIER_FONT,
                file_formats=[OPENTYPE_FILE])


BDF_FILE, BDF_FONT = make_pair(
            [Name('BDF', OFFICIAL_NAME | PREFERRED_NAME | ABBREVIATION),
             Name('Glyph Bitmap Distribution Format',
                  OFFICIAL_NAME | FULL_NAME)],
            icon='bdf', category=BITMAP_FONT)


PCF_FILE, PCF_FONT = make_pair(
            [Name('PCF', OFFICIAL_NAME | PREFERRED_NAME | ABBREVIATION),
             Name('Portable Compiled Font',
                  OFFICIAL_NAME | FULL_NAME)],
            icon='pcf', category=BITMAP_FONT)

SNF_FILE, SNF_FONT = make_pair(
            [Name('SNF', OFFICIAL_NAME | PREFERRED_NAME | ABBREVIATION),
             Name('Server Normal Format',
                  OFFICIAL_NAME | FULL_NAME)],
            icon='snf', category=BITMAP_FONT)


PFR_FILE, PFR_FONT = make_pair(
            [Name('PFR', OFFICIAL_NAME | PREFERRED_NAME | ABBREVIATION),
             Name('Portable Font Resource', OFFICIAL_NAME | FULL_NAME),
             Name('TrueDoc', REGISTERED, entities=[BITSTREAM])],
            icon='pfr', category=OUTLINE_FONT,
            developers=[BITSTREAM])


FNT_FILE, FNT_FONT = make_pair(
            [Name('Windows FNT', UNOFFICIAL_NAME)],
            icon='fnt', category=BITMAP_FONT,
            developers=[MICROSOFT])


PSF_FILE, PSF_FONT = make_pair(
            [Name('PSF', OFFICIAL_NAME | PREFERRED_NAME | ABBREVIATION),
             Name('PC Screen Font', OFFICIAL_NAME | FULL_NAME)],
            icon='psf', category=BITMAP_FONT)

SPEEDO_FILE, SPEEDO_FONT = make_pair(
            [Name('Speedo', OFFICIAL_NAME | PREFERRED_NAME | ABBREVIATION,
                  entities=[BITSTREAM])],
            icon='speedo', category=OUTLINE_FONT,
            developers=[BITSTREAM])


LEGACY_FILE, LEGACY_FONT = make_pair(
            [Name(N_('Legacy application-specific font'), UNOFFICIAL_NAME)],
            icon='legacy', category=Likely(BITMAP_FONT))



METAFONT_FILE, METAFONT_FONT = make_pair(
            [Name('Metafont', OFFICIAL_NAME | PREFERRED_NAME),
             Name('TeX font')],
            icon='metafont', category=STROKE_FONT)


