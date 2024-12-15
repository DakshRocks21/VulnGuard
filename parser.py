import os
from tree_sitter import Language, Parser
import tree_sitter_python as tspython

class CodeParser:
    def __init__(self):
        # Initialize tree-sitter
        self.PY_LANGUAGE = Language(tspython.language())
        self.parser = Parser(self.PY_LANGUAGE)

    def get_python_files(self, directory):
        python_files = []
        for root, _, files in os.walk(directory):
            if 'venv' in root.split(os.sep):
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def extract_symbols(self, tree):
        symbols = []
        cursor = tree.walk()
        
        def visit_node():
            node = cursor.node
            if node.type in ['function_definition', 'class_definition']:
                symbols.append(node.child_by_field_name('name').text.decode('utf8'))
            
            if cursor.goto_first_child():
                visit_node()
                while cursor.goto_next_sibling():
                    visit_node()
                cursor.goto_parent()
        
        visit_node()
        return symbols

    def parse(self):
        # Get current directory
        current_dir = os.getcwd()
        python_files = self.get_python_files(current_dir)
        
        all_symbols = []
        
        # Process each Python file
        for file_path in python_files:
            if not file_path.endswith('.py'):
                continue
            with open(file_path, 'rb') as file:
                content = file.read()
                tree = self.parser.parse(content)
                file_symbols = self.extract_symbols(tree)
                all_symbols.extend(file_symbols)
        
        return all_symbols

if __name__ == '__main__':
    parser = CodeParser()
    symbols = parser.parse()
    for symbol in symbols:
        print(symbol)