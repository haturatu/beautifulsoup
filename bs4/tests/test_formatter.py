from bs4.element import Tag
from bs4.testing import SoupTest
from bs4.formatter import (
    Formatter,
    HTMLFormatter,
    XMLFormatter,
)

class TestFormatter(SoupTest):

    def test_default_attributes(self):
        # Test the default behavior of Formatter.attributes().
        formatter = Formatter()
        tag = Tag(name="tag")
        tag['b'] = 1
        tag['a'] = 2

        # Attributes come out sorted by name. In Python 3, attributes
        # normally come out of a dictionary in the order they were
        # added.
        self.assertEquals([('a', 2), ('b', 1)], formatter.attributes(tag))

        # This works even if Tag.attrs is None, though this shouldn't
        # normally happen.
        tag.attrs = None
        self.assertEquals([], formatter.attributes(tag))
        
    def test_sort_attributes(self):
        # Test the ability to override Formatter.attributes() to,
        # e.g., disable the normal sorting of attributes.
        class UnsortedFormatter(Formatter):
            def attributes(self, tag):
                self.called_with = tag
                for k, v in sorted(tag.attrs.items()):
                    if k == 'ignore':
                        continue
                    yield k,v

        soup = self.soup('<p cval="1" aval="2" ignore="ignored"></p>')
        formatter = UnsortedFormatter()
        decoded = soup.decode(formatter=formatter)

        # attributes() was called on the <p> tag. It filtered out one
        # attribute and sorted the other two.
        self.assertEquals(formatter.called_with, soup.p)
        self.assertEquals(u'<p aval="2" cval="1"></p>', decoded)

    def test_empty_attributes_are_booleans(self):
        # Test the behavior of empty_attributes_are_booleans as well
        # as which Formatters have it enabled.
        
        for name in ('html', 'minimal', None):
            formatter = HTMLFormatter.REGISTRY[name]
            self.assertEquals(False, formatter.empty_attributes_are_booleans)

        formatter = XMLFormatter.REGISTRY[None]
        self.assertEquals(False, formatter.empty_attributes_are_booleans)

        formatter = HTMLFormatter.REGISTRY['html5']
        self.assertEquals(True, formatter.empty_attributes_are_booleans)

        # Verify that the constructor sets the value.
        formatter = Formatter(empty_attributes_are_booleans=True)
        self.assertEquals(True, formatter.empty_attributes_are_booleans)

        # Now demonstrate what it does to markup.
        for markup in (
                "<option selected></option>",
                '<option selected=""></option>'
        ):
            soup = self.soup(markup)
            for formatter in ('html', 'minimal', 'xml', None):
                self.assertEquals(
                    b'<option selected=""></option>',
                    soup.option.encode(formatter='html')
                )
                self.assertEquals(
                    b'<option selected></option>',
                    soup.option.encode(formatter='html5')
                )
