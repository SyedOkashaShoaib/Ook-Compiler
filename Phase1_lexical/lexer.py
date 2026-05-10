import sys
import os
import re  # Required for identifier validation

class Token:
    def __init__(self, type, value, index):
        self.type = type
        self.value = value
        self.index = index
        
    def __str__(self): 
        return f'<{self.type}, {self.value}, Line {self.index}>'
        
    def __repr__(self):
        return self.__str__()

def read_Stream(filename):
    if not os.path.isfile(filename):
        print(f"SYSTEM ERROR: file {filename} does not exist. ook out")
        sys.exit(1)
        
    processed_stream = [] 
    with open(filename, 'r') as file_obj:
        for index, line in enumerate(file_obj, start=1): 
            clean_line = line.strip() 

            words_list = clean_line.split() 
            if not words_list:
                continue
            processed_stream.append({ 'index' :  index, 'words' : words_list})        

    return processed_stream

def get_Tocken_Type(word):
    # Standard 9 Commands
    if word == 'Ook. Ook?': return 'MOVE_RIGHT'
    if word == 'Ook? Ook.': return 'MOVE_LEFT'
    if word == 'Ook. Ook.': return 'INCREMENT'
    if word == 'Ook! Ook!': return 'DECREMENT'
    if word == 'Ook. Ook!': return 'READ'
    if word == 'Ook! Ook.': return 'PRINT'
    if word == 'Ook! Ook?': return 'LOOP_START'
    if word == 'Ook? Ook!': return 'LOOP_END'
    if word == 'Ook? Ook?': return 'GIVE_BANANA'
    
    # New Variable Commands
    if word == 'Ook!! Ook!!': return 'DECLARE_VAR'
    if word == 'Ook?? Ook??': return 'JUMP_VAR'
    
    return 'NO COMPRENDE'
    
def tockenize_Stream(line_number, words):
    line_tocken = []
    i = 0
    
    while i < len(words):
        # We need at least 2 words to make ANY valid Ook! command
        if i + 1 >= len(words):
            print(f"LEXICAL ERROR: Unpaired or dangling word '{words[i]}' found at line {line_number}. Ook Ook")
            sys.exit(1)
            
        word1 = words[i]
        word2 = words[i+1]
        word_pair = f"{word1} {word2}"
        
        tocken_type = get_Tocken_Type(word_pair)
        
        if tocken_type == 'NO COMPRENDE':
            print(f"LEXICAL ERROR: Invalid syntax element '{word_pair}' found at line {line_number}. Ook ook")
            sys.exit(1)

        # Handle 3-word Variable Commands
        if tocken_type in ['DECLARE_VAR', 'JUMP_VAR']:
            if i + 2 >= len(words):
                print(f"LEXICAL ERROR: Missing identifier after '{word_pair}' at line {line_number}. Ook ook")
                sys.exit(1)
                
            identifier = words[i+2]
            
            # Validate that the identifier strictly starts with "ook_"
            if not re.match(r'^ook_[a-zA-Z0-9_]+$', identifier):
                print(f"LEXICAL ERROR: Invalid identifier '{identifier}' at line {line_number}. Must start with 'ook_'. Ook ook")
                sys.exit(1)
                
            # Append the command token, and then immediately append the identifier token
            line_tocken.append(Token(tocken_type, word_pair, line_number))
            line_tocken.append(Token('IDENTIFIER', identifier, line_number))
            
            # Skip forward 3 words instead of 2
            i += 3 
            
        # Handle Standard 2-word Commands
        else:
            line_tocken.append(Token(tocken_type, word_pair, line_number))
            i += 2
            
    return line_tocken
    
def run_Lexer(filename):
    file_data = read_Stream(filename)
    
    tocken_stream = []
    
    for line_dict in file_data:
        line_number = line_dict['index']
        words = line_dict['words']
        line_tocken = tockenize_Stream(line_number, words)

        tocken_stream.extend(line_tocken)
        
    last_line = tocken_stream[-1].index if tocken_stream else 1
    eof_tocken = Token('EOF', 'end of file', last_line + 1)
    tocken_stream.append(eof_tocken)
    
    return tocken_stream 

if __name__ == "__main__":
    if len(sys.argv) < 2:  
        print("SYSTEM ERROR: filename not provided. ook out")
        sys.exit(1)
        
    target_filename = sys.argv[1]
    final_tocken_stream = run_Lexer(target_filename)
    
    print("\n--- PHASE 1: TOKEN STREAM RECIEVED ---")
    for t in final_tocken_stream:
        print(t)
    print("--------------------------------------\n")