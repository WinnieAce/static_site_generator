import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode, markdown_to_html_node, extract_title

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("p", "This is a paragraph")
        node2 = HTMLNode("p", "This is a paragraph")
        self.assertEqual(node, node2)
        
    def test_repr(self):
        node = HTMLNode("p", "This is a paragraph")
        self.assertEqual(repr(node), "HTMLNode(p, This is a paragraph, None, None)")
        
    def test_repr_with_children(self):
        node = HTMLNode("div", None, [HTMLNode("p", "This is a paragraph")])
        self.assertEqual(repr(node), "HTMLNode(div, None, [HTMLNode(p, This is a paragraph, None, None)], None)")
        
    def test_not_eq(self):
        node = HTMLNode("p", "This is a paragraph")
        node2 = HTMLNode("p", "This is a paragraph", [HTMLNode("p", "This is a paragraph")])
        self.assertNotEqual(node, node2)
        
    def test_props_to_html(self):
        node = HTMLNode("img", None, None, {"src": "http://www.google.com"})
        self.assertEqual(node.props_to_html(), 'src="http://www.google.com"')
        
    def test_props_to_html_none(self):      
        node = HTMLNode("img", None)
        self.assertEqual(node.props_to_html(), "")
        
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        
    def test_parent_to_html_div(self):
        node = ParentNode("div", [LeafNode("p", "Hello, world!")])
        self.assertEqual(node.to_html(), "<div><p>Hello, world!</p></div>")
        
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
        
    def test_parent_to_html_no_tag(self):
        node = ParentNode(None, [LeafNode("p", "Hello, world!")])
        with self.assertRaises(ValueError):
            node.to_html()
            
    def test_parent_to_html_many_children(self):
        node = ParentNode("div", [LeafNode("p", "Hello, world!"), LeafNode("p", "Hello, world!")])
        self.assertEqual(node.to_html(), "<div><p>Hello, world!</p><p>Hello, world!</p></div>")
        
    def test_parent_to_html_many_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node, grandchild_node])
        parent_node = ParentNode("div", [child_node, child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b><b>grandchild</b></span><span><b>grandchild</b><b>grandchild</b></span></div>",
        )
        
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
        
    def test_extract_title(self):
        md = """
# Title here
This is **bolded** paragraph
text in a p
tag here    
"""
        title = extract_title(md)
        self.assertEqual(title, "Title here") 
        
    def test_extract_title_no_title(self):
        md = """
This is **bolded** paragraph
text in a p tag here
"""
        with self.assertRaises(Exception):
            extract_title(md)
            