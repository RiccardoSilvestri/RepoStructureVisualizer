import os
import tkinter as tk
from tkinter import filedialog

def should_ignore_folder(folder_name):
    ignore_folders = {
        # IDE e Editor
        '.idea', '.vscode', '.vs', 'nbproject', '.settings', '.metadata', 'xcuserdata',
        '*.xcworkspace', '*.xcodeproj/xcuserdata', '.history', '.sublime-workspace',
        '.ropeproject', '.vim', 'emacs.d', '.spacemacs.d', '.kdev4', '.komodoproject',
        
        # Version Control
        '.git', '.svn', '.hg', 'CVS', '.bzr',
        
        # Environments and Dependencies
        'env', 'venv', '.venv', 'node_modules', 'vendor', 'bower_components', 'jspm_packages',
        '__pypackages__', '.pytest_cache', '.mypy_cache', '.yarn', 'Pods', 'DerivedData',
        'elm-stuff', '_esy', '.cargo', '.dub', '.dart_tool', '.flutter-plugins', '.pub-cache',
        '.clj-kondo', '.lsp', '.shadow-cljs', '.bloop', '.metals', '.ammonite', '.ensime_cache',
        '.bsp', '.gradle', '.mvn', '.lein-*', '.nvm', '.npm', '.pnpm', '.yvm',
        
        # Build e Output
        'build', 'dist', 'out', 'bin', 'obj', 'target', 'deps', '_build', 'release',
        'cmake-build-*', 'dist-ssr', 'dist-server', '.build', 'out-tsc', 'Debug', 'Release',
        'x64', 'ipch', '.externalNativeBuild', 'captures', 'generated', 'compiled',
        
        # Cache e Temp
        '.cache', '.sass-cache', '.parcel-cache', '.nyc_output', '.jest-cache', '.fusebox',
        '.temp', '.tmp', '.turbo', '.rush', '.lazy', '.eslintcache', '.stylelintcache',
        
        # Testing e Coverage
        'coverage', '.jest', 'lcov-info', '.nyc_output', '.allure', '.pytest',
        
        # Framework and Library
        '.next', '.nuxt', 'public', '.expo', '.svelte-kit', '.quasar', '.astro', '.serverless',
        '.terraform', '.terragrunt-cache', '.nextflow', '.scrapy', '.spago', '.redwood',
        '.angular', '.vuepress', '.docusaurus', '.gatsby', '.hexo', '.jekyll', '.middleman',
        '.react-static', '.sapper', '.stencil', '.storybook', '.vite', '.webpack',
        
        # Other
        '.ipynb_checkpoints', '.hypothesis', 'wwwroot', '.replit', '.Trash', 'lost+found',
        '.direnv', '.envs', '.cache', '.logs', '.pids', '.ssh', '.vagrant', '.vscode-test',
        '.vsconfig', '.vspscc', '.vssscc', '.vsix', '.vscodeignore', '.vsixmanifest',
        
        # OS and System Generated
        '.DS_Store', 'Thumbs.db', 'Desktop.ini', '$RECYCLE.BIN', '.Spotlight-V100', '.TemporaryItems',
        
        # Cloud and Infrastructure
        '.serverless', '.cdk.out', '.pulumi', '.sst', '.amplify', '.aws-sam', '.cloudformation',
        
        # Database and Data
        '.sqlite', '.index', '.leveldb', '.rocksdb', '.mongodb', '.mysql', '.postgres',
        
        # Specific Languages
        '.classpath', '.project', '.factorypath', '.apt_generated',
        '.cquery_results', '.ccls-cache',
        '.deps', '.libs', '.aux',
        '.stack-work', 'dist-newstyle',
        '_opam', '_build',
        '.phpintel', '.phpunit.result.cache',
        '.rspec', '.ruby-version', '.ruby-gemset',
        '.swc', '.tsbuildinfo',
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

def get_language_from_extension(file_name):
    extension_to_language = {
        '.1c': '1c', '.1c': '1c',
        '.4d': '4d',
        '.abap': 'sap-abap', '.abnf': 'abnf',
        '.ada': 'ada', '.ak': 'aiken', '.apache': 'apache',
        '.applescript': 'applescript', '.arcade': 'arcade',
        '.asciidoc': 'asciidoc', '.adoc': 'asciidoc',
        '.avrasm': 'avrasm', '.actionscript': 'actionscript',
        '.as': 'actionscript', '.alan': 'alan', '.asc': 'angelscript',
        '.armasm': 'armasm', '.arduino': 'arduino', '.ino': 'arduino',
        
        '.py': 'python', '.gyp': 'python',
        '.js': 'javascript', '.jsx': 'javascript',
        '.java': 'java', '.jsp': 'java',
        '.cpp': 'cpp', '.hpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
        '.c': 'c', '.h': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby', '.gemspec': 'ruby', '.podspec': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin', '.kts': 'kotlin',
        '.pl': 'perl', '.pm': 'perl',
        '.sh': 'bash', '.zsh': 'bash',
        '.ps1': 'powershell', '.ps': 'powershell',
        '.bat': 'dos', '.cmd': 'dos',
        '.lua': 'lua',
        '.r': 'r',
        '.dart': 'dart',
        '.hs': 'haskell',
        '.scala': 'scala',
        '.ex': 'elixir', '.exs': 'elixir',
        '.erl': 'erlang',
        '.sql': 'sql',
        '.fs': 'fsharp', '.fsx': 'fsharp',
        '.clj': 'clojure',
        '.groovy': 'groovy',
        '.d': 'd',
        '.ml': 'ocaml',
        '.pas': 'pascal',
        '.vbs': 'vbscript',
        '.asm': 'x86asm',
        
        '.html': 'html', '.xhtml': 'html',
        '.css': 'css', '.scss': 'scss',
        '.md': 'markdown', '.mkd': 'markdown', '.mkdn': 'markdown',
        '.xml': 'xml', '.svg': 'xml', '.atom': 'xml', '.rss': 'xml',
        '.json': 'json', '.jsonc': 'json',
        '.yaml': 'yaml', '.yml': 'yaml',
        '.toml': 'ini', '.ini': 'ini',
        '.haml': 'haml',
        '.hbs': 'handlebars',
        '.ts': 'typescript', '.tsx': 'typescript',
        '.svelte': 'svelte',
        
        '.dockerfile': 'docker', '.docker': 'docker',
        '.nginx': 'nginx',
        '.cmake': 'cmake',
        '.makefile': 'makefile', '.mk': 'makefile',
        '.txt': 'plaintext', '.text': 'plaintext',
        '.diff': 'diff',
        '.log': 'accesslog',
        '.conf': 'nginx',
        '.zig': 'zig',
        '.odin': 'odin',
        '.v': 'verilog',
        '.cshtml': 'cshtml',
        '.tf': 'terraform',
        '.rsl': 'rsl',
        '.sol': 'solidity',
        '.stl': 'structured-text',
    
    }
    _, extension = os.path.splitext(file_name)
    return extension_to_language.get(extension, 'text')

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
                language = get_language_from_extension(file)
                content += f"\n```{language}\n{file_content}\n```\n"
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
