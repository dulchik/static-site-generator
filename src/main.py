from textnode import TextNode, TextType
import os
import shutil
from markdown_blocks import markdown_to_html_node
from pathlib import Path
import sys

path_to_static = "./static"
path_to_docs = "./docs"
path_to_template = "./template.html"
path_to_content = "./content"

basepath = sys.argv[0]


def main():
    if os.path.exists(path_to_docs):
       shutil.rmtree(path_to_docs)

    copy_dir(path_to_static, path_to_docs)
 
    generate_pages_recursive(path_to_content, path_to_template, path_to_docs, basepath)

def copy_dir(src_path, dst_path):
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)

    for item in os.listdir(src_path):
        curr_path = os.path.join(src_path, item)
        dest_path = os.path.join(dst_path, item)
        if os.path.isfile(curr_path):
            shutil.copy(curr_path, dst_path)
        else:
            copy_dir(curr_path, dest_path)

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:]
    raise Exception("No Title found")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    markdown_file = open(from_path).read()
    template_file = open(template_path).read()

    title = extract_title(markdown_file)
    html_string = markdown_to_html_node(markdown_file).to_html()

    template_file = template_file.replace("{{ Title }}", title)
    template_file = template_file.replace("{{ Content }}", html_string)

    template_file = template_file.replace('href="/"', f'href="{basepath}"')
    template_file = template_file.replace('src="/"', f'src="{basepath}"')
    
    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    to_file = open(dest_path, "w")
    to_file.write(template_file)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):

    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        if os.path.isfile(from_path):
            dest_path = Path(dest_path).with_suffix(".html")
            generate_page(from_path, template_path, dest_path, basepath)
        else:
            generate_pages_recursive(from_path, template_path, dest_path, basepath)
    
            
if __name__ == "__main__":
    main()
