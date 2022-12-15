import os
import sys

from CompLexer import CalcLexer
from CompParser import CalcParser

lexer = CalcLexer()
parser = CalcParser()

def main():
    args = len(sys.argv)
    if args != 3:
        print("Invalid arguments! Correct usage: python CompMain.py INPUT_FILE OUTPUT_FILE")
        return
    
    with open(sys.argv[1], mode='r') as input_file:
        text = input_file.read()
    
    output_commands = parser.parse(lexer.tokenize(text))

    output_name = sys.argv[2]
    os.makedirs(os.path.dirname(output_name), exist_ok=True)

    with open(output_name, "w") as output_file:
        for code in output_commands:
            output_file.write(code + "\n")
        output_file.write("HALT")


if __name__ == "__main__":
    main()