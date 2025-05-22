from enum import Enum

from htmlnode import ParentNode
from markdown import text_to_textnodes
from textnode import text_node_to_html_node, TextNode, TextType

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    ULIST = "unordered_list"
    OLIST = "ordered_list"


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    clean_blocks = []

    for block in blocks:
        if block == "":
            continue
        clean_blocks.append(block.strip())

    return clean_blocks

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

def block_to_html_node(block):
    block_type = block_to_block_type(block)

    if block_type == BlockType.PARAGRAPH:
        lines = block.split("\n")
        paragraph = " ".join(lines)
        children = text_to_children(paragraph)
        return ParentNode("p", children)

    if block_type == BlockType.HEADING:
        level = 0
        for char in block:
            if char == "#":
                level += 1
            else:
                break
        if level + 1 >= len(block):
            raise ValueError(f"Invalid heading level: {level}")
        text = block[level + 1:]
        children = text_to_children(text)
        return ParentNode(f"h{level}", children)
    
    if block_type == BlockType.CODE:
        if not block.startswith("```") or not block.endswith("```"):
            raise ValueError("Invalid code block")
        text = block[4:-3]
        raw_text_node = TextNode(text, TextType.TEXT)
        child = text_node_to_html_node(raw_text_node)
        code = ParentNode("code", [child])
        return ParentNode("pre", [code])

    if block_type == BlockType.OLIST:
        items = block.split("\n")
        html_items = []
        for item in items:
            text = item[3:]
            children = text_to_children(text)
            html_items.append(ParentNode("li", children))
        return ParentNode("ol", html_items)

    if block_type == BlockType.ULIST:
        items = block.split("\n")
        html_items = []
        for item in items:
            text = item[2:]
            children = text_to_children(text)
            html_items.append(ParentNode("li", children))
        return ParentNode("ul", html_items)

    if block_type == BlockType.QUOTE:
        lines = block.split("\n")
        new_lines = []
        for line in lines:
            if not line.startswith(">"):
                raise ValueError("Invalid quote block")
            new_lines.append(line.lstrip(">").strip())
        content = " ".join(new_lines)
        children = text_to_children(content)
        return ParentNode("blockquote", children)
