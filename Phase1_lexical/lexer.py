import sys
import os
class Token:
    def __init__(self, type, value, index):
        self.type = type
        self.value = value
        self.index = index
    def __str__(self): #this is called when we print a token object
        return f'<{self.type}, {self.value}, Line {self.index}>'
    def __repr__(self):
        return self.__str__()
def read_Stream():
    if len(sys.argv) < 2:  #chekc if filename is provided
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)
    filename = sys.argv[1]

    if not os.path.isfile(filename) :   #incorrect filename, path 
        print(f"SYSTEM ERROR: file {filename} does not exist. ook out")
        sys.exit(1)
    processed_stream = [] #list of dictionaries
    with open(filename, 'r') as file_obj:
        for index, line in enumerate(file_obj, start=1): #we need line numbers for error handling 
            clean_line = line.strip() #remove leading and ending whitespaces 

            words_list = clean_line.split() #split by whitespace
            if not words_list:
                continue
            processed_stream.append({ 'index' :  index, 'words' : words_list})        

    return processed_stream
# Ook? Ook?
# Give the Memory Pointer a banana.
def get_Tocken_Type(word):
    if word == 'Ook. Ook?':
        return 'MOVE_RIGHT'
    if word == 'Ook? Ook.':
        return 'MOVE_LEFT'
    if word == 'Ook. Ook.':
        return 'INCREMENT'
    if word == 'Ook! Ook!':
        return 'DECREMENT'
    if word == 'Ook. Ook!':
        return 'READ'
    if word == 'Ook! Ook.':
        return 'PRINT'
    if word == 'Ook! Ook?': #while (pointer != 0) {
        return 'LOOP_START'
    if word == 'Ook? Ook!':
        return 'LOOP_END'
    if word == 'Ook? Ook?':
        return 'GIVE_BANANA'
    return 'NO COMPRENDE'

    
def tockenize_Stream(line_number, words):
    if len(words) % 2 != 0:
        print(f"LEXICAL ERROR: Unpaired Ook: '{words[-1]}' found at line {line_number}. Ook Ook")
        sys.exit(1)
    
    line_tocken = []
    for i in range(0, len(words), 2):
        word1 = words[i]
        word2 = words[i+1]
        word_pair = f"{word1} {word2}"
        # print(word_pair)
        type = get_Tocken_Type(word_pair)
        # print(type)
        if type == 'NO COMPRENDE':
            print(f"LEXICAL ERROR: Invalid syntax element '{word_pair}' found at line {line_number}. Ook ook")
            sys.exit(1)

        line_tocken.append(Token(type, word_pair, line_number))
        # print(line_tocken)
    return line_tocken

    
def run_Lexer():
    file_data = read_Stream()
    # print(file_data)

    tocken_stream = []
    
    for dict in file_data:
        line_number = dict['index']
        words = dict['words']
        line_tocken = tockenize_Stream(line_number, words)

        tocken_stream.extend(line_tocken)
    print(tocken_stream) 

run_Lexer()