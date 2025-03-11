import os
import shutil
import sys
from htmlnode import markdown_to_html_node, HTMLNode, LeafNode, ParentNode, extract_title

basepath = sys.argv[1] if len(sys.argv) > 1 else '/' 

def copy_static(source, destination):
    # First, clear the destination if it exists
    if os.path.exists(destination):
        shutil.rmtree(destination)
    
    # Create the destination directory
    os.mkdir(destination)
    
    # Now we'll define our recursive function
    def copy_recursive(current_source, current_dest):
        # List all items in the current source directory
        for item in os.listdir(current_source):
            # Get full paths
            source_path = os.path.join(current_source, item)
            dest_path = os.path.join(current_dest, item)
            
            # If it's a file, copy it
            if os.path.isfile(source_path):
                print(f"Copying file: {source_path} to {dest_path}")
                shutil.copy(source_path, dest_path)
            # If it's a directory, create it and recurse
            else:
                print(f"Creating directory: {dest_path}")
                os.mkdir(dest_path)
                # Recursive call for subdirectory
                copy_recursive(source_path, dest_path)
    
    # Start the recursive process
    copy_recursive(source, destination)

def main():
    copy_static("static", "docs")
    generate_pages_recursive('content', 'template.html', 'docs', basepath)
    
def generate_page(from_path, template_path, dest_path, basepath):
    if not os.path.exists(from_path):
        raise ValueError(f"File {from_path} does not exist")
    if not os.path.exists(template_path):
        raise ValueError(f"File {template_path} does not exist")
    
    print(f'Generating page from {from_path} using {template_path} to {dest_path}')
    with open(from_path, 'r') as f:
        contents = f.read()
    with open(template_path, 'r') as f:
        template = f.read()

    contents_html_nodes = markdown_to_html_node(contents)
    print('nodes: ', contents_html_nodes)
    contents_html = contents_html_nodes.to_html()
    print('html: ', contents_html)
    content_title = extract_title(contents)
    final_page = template.replace("{{ Content }}", contents_html).replace("{{ Title }}", content_title)
            
    final_page = final_page.replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}').replace("href='/", f"href='{basepath}").replace("src='/", f"src='{basepath}")

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(final_page)
    
def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    directory_items = os.listdir(dir_path_content)
    for item in directory_items:
        full_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item.replace('.md', '.html') if item.endswith('.md') else item)
        
        if os.path.isdir(full_path):
            os.makedirs(dest_path, exist_ok=True)
            generate_pages_recursive(full_path, template_path, dest_path, basepath)
        elif os.path.isfile(full_path):
            if item.endswith('.md'):
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                generate_page(full_path, template_path, dest_path, basepath)
    
    
if __name__ == "__main__":
    main()