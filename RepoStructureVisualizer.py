import os
import tkinter as tk
from tkinter import filedialog

def should_ignore_folder(folder_name):
    ignore_folders = {
        '.idea', '__pycache__', '.vscode', '.vs', 'nbproject', '.settings',
        '.git', '.svn', '.hg',
        'env', 'venv', '.venv', 'node_modules', 'vendor', 'bower_components', 'jspm_packages',
        'build', 'dist', 'out', 'bin', 'obj', 'target', 'deps', '_build', 'release',
        '.cache', '.npm', '.sass-cache', '.gradle', 'logs', 'temp', 'tmp',
        'coverage', '.jest',
        '.next', '.nuxt', 'public'
    }
    return folder_name in ignore_folders

def get_project_structure(root_folder):
    structure = {}
    for root, dirs, files in os.walk(root_folder, topdown=True):
        dirs[:] = [d for d in dirs if not should_ignore_folder(d)]
        rel_path = os.path.relpath(root, root_folder)
        structure[rel_path] = files.copy()
    return structure

def build_nested_tree(project_structure):
    tree = {'files': [], 'subfolders': {}}
    for path, files in project_structure.items():
        if path == '.':
            tree['files'] = files
            continue
        parts = path.split(os.sep)
        current = tree
        for part in parts:
            if part not in current['subfolders']:
                current['subfolders'][part] = {'files': [], 'subfolders': {}}
            current = current['subfolders'][part]
        current['files'] = files
    return tree

def generate_markdown_tree(nested_tree):
    lines = ['```\n', '.\n']
    
    def traverse(node, indent):
        folders = sorted(node['subfolders'].keys())
        files = sorted(node['files'])
        
        for i, folder in enumerate(folders):
            last_folder = i == len(folders) - 1 and not files
            prefix = '└── ' if last_folder else '├── '
            lines.append(f"{indent}{prefix}{folder}/\n")
            new_indent = indent + ('    ' if last_folder else '│   ')
            traverse(node['subfolders'][folder], new_indent)
        
        for i, file in enumerate(files):
            last_file = i == len(files) - 1
            prefix = '└── ' if last_file else '├── '
            lines.append(f"{indent}{prefix}{file}\n")
    
    traverse(nested_tree, '')
    lines.append('```\n\n')
    return ''.join(lines)

def create_markdown_content(project_structure, root_folder):
    content = "# Project Structure\n\n## Directory Tree\n\n"
    nested_tree = build_nested_tree(project_structure)
    content += generate_markdown_tree(nested_tree)
    content += "## File Details\n\n"
    
    def process_folder(node, path, level):
        nonlocal content
        folder_name = os.path.basename(path) if path != '.' else 'Root'
        content += f"{'#' * level} {folder_name}\n"
        
        for file in sorted(node['files']):
            file_path = os.path.join(root_folder, path, file)
            content += f"- `{file}`\n"
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read().strip()
                content += f"\n```python\n{file_content}\n```\n"
            except Exception as e:
                content += f"\n*Error reading {file}: {str(e)}*\n"
        
        if not node['files']:
            content += f"*No files in folder {folder_name}*\n"
        
        for subfolder in sorted(node['subfolders'].keys()):
            new_path = os.path.join(path, subfolder)
            process_folder(node['subfolders'][subfolder], new_path, level + 1)
    
    process_folder(nested_tree, '.', 2)
    return content

def main():
    root = tk.Tk()
    root.withdraw()
    
    folder = filedialog.askdirectory(title="Select Project Folder")
    if not folder:
        print("Operation canceled.")
        return
    
    structure = get_project_structure(folder)
    md_content = create_markdown_content(structure, folder)
    
    output_file = f"{os.path.basename(folder)}_structure.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"File generated: {output_file}")

if __name__ == "__main__":
    main()