from enum import Enum
import re


class BlockType(Enum):
    paragraph = 0
    heading = 1
    code = 2
    quote = 3
    unordered_list = 4
    ordered_list = 5
    
def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    return [block.strip() for block in blocks if block.strip()]

def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block):
        return BlockType.heading
    if block.startswith("```") and block.endswith("```"):
        return BlockType.code
    if block.startswith(">"):
        return BlockType.quote
    if all(line.startswith("- ") for line in block.split("\n")):
        return BlockType.unordered_list
    if all(line.startswith(f"{i+1}. ") for i, line in enumerate(block.split("\n"))):
        return BlockType.ordered_list
    return BlockType.paragraph

def block_to_tag(block):
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.paragraph:
            return "p"
        case BlockType.heading:
            return f"h{len(re.match(r"^(#{1,6}) ", block).group(1))}"
        
        # this needs to be tested in <pre> tag
        case BlockType.code:
            return "code"
        case BlockType.quote:
            return "blockquote"
        
        # each list item needs to have <li> tag 
        case BlockType.unordered_list:
            return "ul"
        case BlockType.ordered_list:
            return "ol"

