from enum import Enum
import re

class TextType(Enum):
    TEXT = 0
    BOLD = 1
    ITALIC = 2
    CODE = 3
    LINK = 4    
    IMAGE = 5
    
class TextNode():
    def __init__(self, text, text_type, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url
        
    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
    

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for old_node in old_nodes:
        # Skip nodes that aren't plain text
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        # Skip nodes that don't contain the delimiter
        if delimiter not in old_node.text:
            new_nodes.append(old_node)
            continue
        
        # Check if delimiter count is odd (unbalanced delimiters)
        delimiter_count = old_node.text.count(delimiter)
        if delimiter_count % 2 != 0:
            raise ValueError("invalid markdown, formatted section not closed")

        # Split the text by the provided delimiter
        sections = old_node.text.split(delimiter)
        
        for i, section in enumerate(sections):
            if not section:
                continue  # Skip empty sections
            if i % 2 == 0:  # Even-indexed sections are plain text
                new_nodes.append(TextNode(section, TextType.TEXT))
            else:  # Odd-indexed sections are the specified text type
                new_nodes.append(TextNode(section, text_type))
    
    return new_nodes

def extract_markdown_images(text):
    link_patter = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")
    matches = link_patter.findall(text)
    return [[f"![{match[0]}]({match[1]})", match[0], match[1]] for match in matches]

def extract_markdown_links(text):
    # Regex to match [text](url) format
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    matches = link_pattern.findall(text)

    # Format the output to include the full markdown, text, and URL
    return [[f"[{match[0]}]({match[1]})", match[0], match[1]] for match in matches]

def split_nodes_generic(old_nodes, extraction_function, node_type):
    new_nodes = []

    for old_node in old_nodes:
        # Skip nodes that aren't plain text
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        # Check for matches using the provided extraction function
        matches = extraction_function(old_node.text)
        if not matches:
            new_nodes.append(old_node)
            continue

        sections = []
        remaining_text = old_node.text
        for match in matches:
            # Extract match components
            markdown = match[0]  # Full markdown (e.g., ![alt](url))
            alt = match[1]       # Alt text or link text
            url = match[2]       # URL (either image or link)

            # Split text into "before", "match", and "after"
            before, _, after = remaining_text.partition(markdown)

                        # Add the "before" section as a plain text node if non-empty
            if before:
                sections.append(TextNode(before, TextType.TEXT))

            # Add the actual match as either a LINK or IMAGE node
            sections.append(TextNode(alt, node_type, url))

            # Update the remaining_text to the "after" section
            remaining_text = after

        # Add the remaining_text as a plain text node if non-empty
        if remaining_text:
            sections.append(TextNode(remaining_text, TextType.TEXT))

        # Append all generated sections to the final list
        new_nodes.extend(sections)

    return new_nodes

def split_nodes_image(old_nodes):
    return split_nodes_generic(old_nodes, extract_markdown_images, TextType.IMAGE)


def split_nodes_link(old_nodes):
    return split_nodes_generic(old_nodes, extract_markdown_links, TextType.LINK)

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes

