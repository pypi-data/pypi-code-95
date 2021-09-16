# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from nereid.testing import NereidTestCase


class TestTranslation(NereidTestCase):
    'Test the Translation Integration with Tryton'

    def setUp(self):
        # Install the test module which has bundled translations which can
        # be used for this test
        trytond.tests.test_tryton.activate_module('nereid_test')

    @with_transaction()
    def test_0010_nereid_template_extraction(self):
        """
        Test translation extaction from nereid templates
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        count_before = IrTranslation.search([
                ('type', '=', 'nereid_template')
                ], count=True)
        self.assertEqual(count_before, 0)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        count_after = IrTranslation.search([
                ('type', '=', 'nereid_template')
                ], count=True)
        self.assertTrue(count_after > count_before)

    @with_transaction()
    def test_0020_nereid_code_extraction(self):
        """
        Ensure that templates are extracted from the code
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        count_before = IrTranslation.search([
                ('type', '=', 'nereid')
                ], count=True)
        self.assertEqual(count_before, 0)

        # Set the nereid translations alone
        set_wizard.set_nereid()

        count_after = IrTranslation.search([
                ('type', '=', 'nereid')
                ], count=True)
        self.assertTrue(count_after > count_before)

    @with_transaction()
    def test_0030_wtforms_builtin_extraction(self):
        """
        Ensure that the builtin messages from wtforms are also extracted
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        count_before = IrTranslation.search([
                ('type', '=', 'wtforms')
                ], count=True)
        self.assertEqual(count_before, 0)

        # Set the wtforms translations alone
        set_wizard.set_wtforms()

        count_after = IrTranslation.search([
                ('type', '=', 'wtforms')
                ], count=True)
        self.assertTrue(count_after > count_before)

    @with_transaction()
    def test_0040_template_gettext_using_(self):
        """
        Test for gettext without comment using _
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        # gettext with no comments and using _
        translation, = IrTranslation.search([
                ('type', '=', 'nereid_template'),
                ('module', '=', 'nereid_test'),
                ('src', '=', 'gettext')
                ])
        self.assertEqual(translation.comments, None)
        self.assertEqual(translation.res_id, 7)

    @with_transaction()
    def test_0050_template_gettext_2(self):
        """
        Test for gettext with comment before it
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        translation, = IrTranslation.search([
                ('type', '=', 'nereid_template'),
                ('module', '=', 'nereid_test'),
                ('src', '=', 'gettext with comment b4')
                ])
        self.assertEqual(translation.comments, translation.src)
        self.assertEqual(translation.res_id, 10)

    @with_transaction()
    def test_0060_template_gettext_3(self):
        """
        Test for gettext with comment inline
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        translation, = IrTranslation.search([
                ('type', '=', 'nereid_template'),
                ('module', '=', 'nereid_test'),
                ('src', '=', 'gettext with comment inline')
                ])
        self.assertEqual(translation.comments, translation.src)
        self.assertEqual(translation.res_id, 12)

    # unwrapped gettext and ngettext functionality removed (#4135)
    #
    #@with_transaction()
    #def test_0070_template_gettext_4(self):
    #    """
    #    Test for gettext using gettext instead of _
    #    """
    #    pool = Pool()
    #    TranslationSet = pool.get('ir.translation.set', type='wizard')
    #    IrTranslation = pool.get('ir.translation')

    #    session_id, _, _ = TranslationSet.create()
    #    set_wizard = TranslationSet(session_id)

    #    # Set the nereid_template translations alone
    #    set_wizard.set_nereid_template()

    #    translation, = IrTranslation.search([
    #            ('type', '=', 'nereid_template'),
    #            ('module', '=', 'nereid_test'),
    #            ('src', '=', 'Hello World!')
    #            ])
    #    self.assertEqual(translation.comments, None)
    #    self.assertEqual(translation.res_id, 17)

    # unwrapped gettext and ngettext functionality removed (#4135)
    #
    #@with_transaction()
    #def test_0080_template_ngettext(self):
    #    """
    #    Test for ngettext
    #    """
    #    pool = Pool()
    #    TranslationSet = pool.get('ir.translation.set', type='wizard')
    #    IrTranslation = pool.get('ir.translation')

    #    session_id, _, _ = TranslationSet.create()
    #    set_wizard = TranslationSet(session_id)

    #    # Set the nereid_template translations alone
    #    set_wizard.set_nereid_template()

    #    translation, = IrTranslation.search([
    #            ('type', '=', 'nereid_template'),
    #            ('module', '=', 'nereid_test'),
    #            ('src', '=', '%(num)d apple')
    #            ])
    #    self.assertEqual(translation.res_id, 20)

    #    # Look for plural
    #    translation, = IrTranslation.search([
    #            ('type', '=', 'nereid_template'),
    #            ('module', '=', 'nereid_test'),
    #            ('src', '=', '%(num)d apples')
    #            ])
    #    self.assertEqual(translation.res_id, 20)

    @with_transaction()
    def test_0090_template_trans_tag(self):
        """
        Test for {% trans %}Hola {{ user }}!{% endtrans %} tag

        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        # XXX: See how {{ user }} changed to %(user)s
        translation, = IrTranslation.search([
                ('type', '=', 'nereid_template'),
                ('module', '=', 'nereid_test'),
                ('src', '=', 'Hello %(username)s!'),
                ])
        self.assertEqual(translation.comments,
            'Translation with trans tag')
        self.assertEqual(translation.res_id, 23)

    @with_transaction()
    def test_0100_template_trans_tag_with_expr(self):
        """
        Test for
        {% trans user=user.username %}Hello {{ user }}!{% endtrans %} tag
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        # XXX: See how {{ user }} changed to %(user)s
        translation, = IrTranslation.search([
                ('type', '=', 'nereid_template'),
                ('module', '=', 'nereid_test'),
                ('src', '=', 'Hello %(name)s!')
                ])
        self.assertEqual(translation.comments,
            'Translation with an expression')
        self.assertEqual(translation.res_id, 26)

    @with_transaction()
    def test_0110_template_trans_tag_plural(self):
        """
        Test for

        {% trans count=list|length %}
        There is {{ count }} {{ name }} object.
        {% pluralize %}
        There are {{ count }} {{ name }} objects.
        {% endtrans %}

        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        IrTranslation = pool.get('ir.translation')

        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)

        # Set the nereid_template translations alone
        set_wizard.set_nereid_template()

        translation, = IrTranslation.search([
                ('type', '=', 'nereid_template'),
                ('module', '=', 'nereid_test'),
                ('src', 'ilike', '%There is %(count)s %(objname)s object.%'),
                ])
        self.assertEqual(translation.comments,
            'trans tag with pluralisation')
        self.assertEqual(translation.res_id, 29)

        # now look for the plural
        translation, = IrTranslation.search([
            ('type', '=', 'nereid_template'),
            ('module', '=', 'nereid_test'),
            ('src', 'ilike', '%There are %(count)s %(objname)s objects.%'),
        ])
        self.assertEqual(
            translation.comments, 'trans tag with pluralisation'
        )
        self.assertEqual(translation.res_id, 29)

    @with_transaction()
    def test_0200_translation_clean(self):
        """
        Check if the cleaning of translations work
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        TranslationClean = pool.get('ir.translation.clean', type='wizard')
        IrTranslation = pool.get('ir.translation')
        IRModule = pool.get('ir.module')

        # First create all the translations
        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)
        set_wizard.transition_set_()

        # Uninstall nereid_test and there should be no translations
        # belonging to that module with type as nereid or
        # nereid_template
        nereid_test, = IRModule.search([('name', '=', 'nereid_test')])
        nereid_test.state = 'not activated'
        nereid_test.save()

        session_id, _, _ = TranslationClean.create()
        clean_wizard = TranslationClean(session_id)
        clean_wizard.transition_clean()

        count = IrTranslation.search([
                ('module', '=', 'nereid_test'),
                ('type', 'in', ('nereid', 'nereid_template'))
                ], count=True)
        self.assertEqual(count, 0)

    @with_transaction()
    def test_0300_translation_update(self):
        """
        Check if the update does not break this functionality
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        TranslationUpdate = pool.get('ir.translation.update', type='wizard')
        IrTranslation = pool.get('ir.translation')
        IRLanguage = pool.get('ir.lang')

        # First create all the translations
        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)
        set_wizard.transition_set_()

        # set an additional language as translatable
        new_lang, = IRLanguage.search([
                ('translatable', '=', False)
                ], limit=1)
        new_lang.translatable = True
        new_lang.save()

        count_before = IrTranslation.search([], count=True)

        # Now update the translations
        session_id, _, _ = TranslationUpdate.create()
        update_wizard = TranslationUpdate(session_id)

        update_wizard.start.language = new_lang
        update_wizard.do_update(update_wizard.update.get_action())

        # check the count now
        count_after = IrTranslation.search([], count=True)
        self.assertEqual(count_after, count_before * 2)

    @with_transaction()
    def test_0400_translation_export(self):
        """
        Export the translations and test
        """
        pool = Pool()
        TranslationSet = pool.get('ir.translation.set', type='wizard')
        TranslationUpdate = pool.get('ir.translation.update', type='wizard')
        IrTranslation = pool.get('ir.translation')
        IRLanguage = pool.get('ir.lang')

        # First create all the translations
        session_id, _, _ = TranslationSet.create()
        set_wizard = TranslationSet(session_id)
        set_wizard.transition_set_()

        # set an additional language as translatable
        new_lang, = IRLanguage.search([
                ('translatable', '=', False)
                ], limit=1)
        new_lang.translatable = True
        new_lang.save()

        # Now update the translations
        session_id, _, _ = TranslationUpdate.create()
        update_wizard = TranslationUpdate(session_id)

        update_wizard.start.language = new_lang
        update_wizard.do_update(update_wizard.update.get_action())

        # TODO: Check the contents of the po file
        IrTranslation.translation_export(new_lang.code, 'nereid_test')
        IrTranslation.translation_export(new_lang.code, 'nereid')


def suite():
    "Nereid Translation test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestTranslation))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
