from os import chdir
from treewalker import TreeWalker
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest

chdir(Path(__file__).parent)


# TODO replace the simple class below with actual tests for your code in treewalker
class TestWalker(unittest.TestCase):
    def setUp(self) -> None:
        self.t = TemporaryDirectory()
        self.w = TreeWalker(Path(self.t.name) / 'test_walker.sqlite', rewrite=False)

    def tearDown(self) -> None:
        self.w.close()
        self.t.cleanup()

    def test_version_defined(self):
        try:
            from treewalker import __version__
        except ImportError:
            self.fail('__version__ not in package')

    def test_walk(self):
        self.w.walk('data\\dir')
        self.w.commit()
        self.assertEqual({'sub': {'test.txt': None}, 'test.txt': None}, self.w.get_tree('data\\dir'))

    def test_db_add(self):
        with TreeWalker(Path(self.t.name) / 'test_walker_two.sqlite', rewrite=False) as w:
            w.walk('data\\dir_two')

        self.w.walk('data\\dir')
        self.w.commit()
        self.w.add_db(str(Path(self.t.name) / 'test_walker_two.sqlite'))
        self.w.commit()
        self.assertEqual({
            'data\\dir': {'sub': {'test.txt': None}, 'test.txt': None},
            'data\\dir_two': {'sub2': {'test2.txt': None}, 'test2.txt': None}
        }, self.w.get_tree())

    def test_remove(self):
        self.w.walk('data\\dir')
        self.w.commit()
        self.w.remove('data\\dir\\sub')
        self.assertEqual({'test.txt': None}, self.w.get_tree('data\\dir'))
