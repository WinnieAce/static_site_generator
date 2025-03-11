from blocknode import *
import unittest

class TestBlockNode(unittest.TestCase):
    def test_block_to_block_type_paragraph(self):
        self.assertEqual(block_to_block_type("This is a paragraph"), BlockType.paragraph)
        
    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# This is a heading"), BlockType.heading)
        
    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```\nThis is code\n```"), BlockType.code)
    
    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.quote)
        
    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(block_to_block_type("- This is a list item"), BlockType.unordered_list)
        
    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(block_to_block_type("1. This is a list item"), BlockType.ordered_list) 
        
    def test_block_to_block_type_ordered_list_multiple_items(self):
        self.assertEqual(
            block_to_block_type("1. This is a list item\n2. This is a list item"),
            BlockType.ordered_list,
        )
    