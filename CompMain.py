import os
import sys

from CompLexer import CompLexer
from CompParser import CompParser
from PostManager import PostManager
from precompiler.PreLexer import PreLexer
from precompiler.PreParser import PreParser
from PreManager import PreManager

pre_lexer = PreLexer()
pre_parser = PreParser()
pre_manager = PreManager()
post_manager = PostManager()

lexer = CompLexer()
parser = CompParser()

def main(debug = False):
    args = len(sys.argv)
    if args != 3:
        print("Invalid arguments! Correct usage: python CompMain.py INPUT_FILE OUTPUT_FILE")
        return
    
    with open(sys.argv[1], mode='r') as input_file:
        text = input_file.read()
    

    pre_store, text = pre_parser.parse(pre_lexer.tokenize(text))
    text = pre_manager.optimize_input(text, pre_store)
    parser.manager.initialize_numbers(pre_store.numbers)

    if debug:
        print(text)

    output_commands : list[str] = parser.parse(lexer.tokenize(text))

    output_commands = post_manager.optimize(output_commands)

    output_name = sys.argv[2]
    os.makedirs(os.path.dirname(output_name), exist_ok=True)

    with open(output_name, "w") as output_file:
        for code in output_commands:
            output_file.write(code + ("\n" if "HALT" not in code else ""))


if __name__ == "__main__":
    main(debug=True)