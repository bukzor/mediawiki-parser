# -*- coding: utf8 -*-
from unittest import TestCase as UnitTestCase

from pijnu import makeParser

from mediawiki_parser import preprocessor, raw, text, html

class TestCase(UnitTestCase):
    def assertEquals(self, x, y, *args, **kwargs):
        try:
            return super(TestCase, self).assertEquals(x, y, *args, **kwargs)
        except AssertionError:
            if isinstance(x, basestring) and isinstance(y, basestring):
                import difflib
                print "%s"%x
                print "*****\n%s"%y
                s = difflib.SequenceMatcher(a=x, b=y)
                for opcode in s.get_opcodes():
                    print "%6s a[%d:%d] b[%d:%d]" % opcode
            raise


def setup_module():
    import os
    if os.stat("preprocessor.pijnu").st_mtime - os.stat("preprocessorParser.py").st_mtime > 1:
        preprocessorGrammar = file("preprocessor.pijnu").read()
        makeParser(preprocessorGrammar)

    if os.stat("mediawiki.pijnu").st_mtime - os.stat("mediawikiParser.py").st_mtime > 1:
        mediawikiGrammar = file("mediawiki.pijnu").read()
        makeParser(mediawikiGrammar)


class PreprocessorTestCase(TestCase):
    def _grammar(self, templates):
        """Return a full or partial grammar.

        method_name -- If truthy, the attribute of the full grammar to return

        """
        return preprocessor.make_parser(templates)

    def parsed_equal_string(self, source, result, templates={}):
        self.assertEquals(unicode(self._grammar(templates).parseTest(source).value), result)


class ParserTestCase(TestCase):
    def _preprocessor(self, templates):
        return preprocessor.make_parser(templates)

    def _grammar(self, method_name):
        """Return a full or partial grammar.

        method_name -- If truthy, the attribute of the full grammar to return

        """
        parser = raw.make_parser()

        return getattr(parser, method_name) if method_name else parser

    def parsed_equal_string(self, source, result, method_name, templates={}):
        preprocessed = self._preprocessor(templates).parseTest(source).value
        self.assertEquals(unicode(self._grammar(method_name).parseTest(preprocessed).value), result)

    def parsed_equal_tree(self, source, result, method_name, templates={}):
        preprocessed = self._preprocessor(templates).parseTest(source).value
        self.assertEquals(self._grammar(method_name).parseTest(preprocessed).treeView(), result)


class PostprocessorTestCase(TestCase):
    def _preprocessor(self, templates):
        return preprocessor.make_parser(templates)

    def _grammar(self, method_name, postprocessor_name):
        """Return a full or partial grammar.

        method_name -- If truthy, the attribute of the full grammar to return

        """
        if postprocessor_name == 'html':
            allowed_tags = ['p', 'span', 'b', 'i']
            allowed_autoclose_tags = ['br', 'hr']
            allowed_parameters = ['class', 'style', 'name', 'id', 'scope']
            interwiki = {'en': 'http://en.wikipedia.org/wiki/',
                         'fr': 'http://fr.wikipedia.org/wiki/'}
            namespaces = {'Template':   10,
                          u'Catégorie': 14,
                          'Category':   14,
                          'File':        6,
                          'Image':       6}
            parser = html.make_parser(allowed_tags, allowed_autoclose_tags, allowed_parameters, interwiki, namespaces)
        elif postprocessor_name == 'text':
            parser = text.make_parser()
        else:
            parser = raw.make_parser()
        return getattr(parser, method_name) if method_name else parser

    def parsed_equal_string(self, source, result, method_name, templates={}, postprocessor='raw'):
        preprocessed = self._preprocessor(templates).parseTest(source).value
        self.assertEquals(unicode(self._grammar(method_name, postprocessor).parseTest(preprocessed).leaves()), result)
