from blocknode import markdown_to_blocks, block_to_block_type, block_to_tag, BlockType
from textnode import text_to_textnodes, TextNode, TextType
import re

class HTMLNode:
    def __init__(self, tag = None, value = None, children = None, props = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
        
    def __eq__(self, other):
        return self.tag == other.tag and self.value == other.value and self.children == other.children and self.props == other.props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if self.props is None:
            return ""
        return " ".join([f'{key}="{value}"' for key, value in self.props.items()])
        
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    
# class LeafNode(HTMLNode):
#     def __init__(self, tag, value, props = None):
#         super().__init__(tag, value, None, props)
        
#     def to_html(self):
#         if self.value is None:
#             return ''
#         if self.tag is None:
#             return self.value
#         if self.props is None:
#             return f"<{self.tag}>{self.value}</{self.tag}>"
#         return f"<{self.tag} {self.props_to_html()}>{self.value}</{self.tag}>"
    
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
        
    def to_html(self):
        # Self-closing tag case (like <img>)
        if self.tag in {'img', 'br', 'hr', 'input'}:
            return f"<{self.tag} {self.props_to_html()} />".strip()
        
        # Plain text value (no tag)
        if self.tag is None:
            return self.value or ''
        
        # Normal tag with opening and closing parts
        if self.props is None:
            return f"<{self.tag}>{self.value}</{self.tag}>"
        return f"<{self.tag} {self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = None):
        super().__init__(tag, None, children, props)
        
    def to_html(self):
        if self.tag is None:
            raise ValueError("Parent nodes must have a tag")
        if self.children is None:
            raise ValueError("Parent nodes must have children")
        children_html = "".join([child.to_html() for child in self.children])
        if self.props is None:
            return f"<{self.tag}>{children_html}</{self.tag}>"
        return f"<{self.tag} {self.props_to_html()}>{children_html}</{self.tag}>"
    
def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
        

    
def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_type_and_block = [(block_to_block_type(block), block) for block in blocks]
    parent_node = ParentNode('div', [])
    
    for block_type, block in block_type_and_block:
        tag = block_to_tag(block) 
        
        if block_type == BlockType.paragraph:
            # Replace newlines with spaces for paragraphs
            modified_block = ' '.join(block.split('\n'))
            text_nodes = [text_node_to_html_node(text_node) for text_node in text_to_textnodes(modified_block)]
            parent_node.children.append(ParentNode(tag, text_nodes))
        
        elif block_type == BlockType.heading:
            # Remove the leading hashes and extra spaces
            clean_block = re.sub(r"^#{1,6} ", "", block).strip()
            text_nodes = [text_node_to_html_node(text_node) for text_node in text_to_textnodes(clean_block)]
            parent_node.children.append(ParentNode(tag, text_nodes))
            
        elif block_type == BlockType.quote:
            # Clean each line in the quote block, stripping "> " and whitespace
            clean_block = "\n".join(line.lstrip("> ").strip() for line in block.splitlines())
            
            # Convert cleaned text into text nodes
            text_nodes = [text_node_to_html_node(text_node) for text_node in text_to_textnodes(clean_block)]
            
            # Append the processed block quote
            parent_node.children.append(ParentNode(tag, text_nodes))
                    
        elif block_type == BlockType.code:
            # Just extract the lines between the opening and closing ```
            if block.startswith("```"):
                code_lines = block.split("\n")[1:-1]
                code_content = "\n".join(code_lines) + "\n"  # Add back the final newline
            else:
                code_content = block
            # Get the content inside the code block without the backticks
            # Create a single TextNode without parsing inline markdown
            code_text_node = TextNode(code_content, TextType.TEXT)
            code_html_node = text_node_to_html_node(code_text_node)
            parent_node.children.append(ParentNode('pre', [ParentNode(tag, [code_html_node])]))
            
        elif block_type == BlockType.unordered_list:
            items = block.split('\n')
            list_items = []
            for item in items:
                if item.strip():
                    list_items.append(ParentNode('li', [text_node_to_html_node(text_node) for text_node in text_to_textnodes(item[2:])]))
            parent_node.children.append(ParentNode(tag, list_items))
            
        elif block_type == BlockType.ordered_list:
            items = block.split('\n')
            list_items = []
            for item in items:
                if item.strip():
                    list_items.append(ParentNode('li', [text_node_to_html_node(text_node) for text_node in text_to_textnodes(item[3:])]))
            parent_node.children.append(ParentNode(tag, list_items))
            
        elif block_type == BlockType.heading:
            text_nodes = [text_node_to_html_node(text_node) for text_node in text_to_textnodes(block)]
            parent_node.children.append(ParentNode(tag, text_nodes))
    return parent_node

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line.lstrip("# ").strip('')
    raise Exception("No title found")