import sys
from pathlib import Path

SHORTCUT_SIGNAL = "bindsym"
COMMENT_SIGNAL = "#"
MOD_SIGNAL = "$mod"

## old implementation 
# def tokenize(string):
    
#     if string[:len(SHORTCUT_SIGNAL)] != SHORTCUT_SIGNAL: 
#         raise RuntimeWarning("Tokenizer Received non-shortcut string")

#     shortcut = []
#     shortcut_ending = None
#     comment_beginning = None 
#     string_no_signal = string[1+len(SHORTCUT_SIGNAL):]

#     # loop through the remaintring string
#     for i, letter in enumerate(string_no_signal):

#         # save the key combination for this shortcut
#         if letter == " " and not shortcut_ending:
#             shortcut.append(string_no_signal[:i])
#             shortcut_ending = i

#         if letter == "#":
#             comment_beginning = i
#             break

#     shortcut.append(string_no_signal[shortcut_ending:comment_beginning])

#     if comment_beginning:
#         shortcut.append(string_no_signal[comment_beginning:])

#     return shortcut

# def sort_list(shortcuts):
#     # x[0] is the key combination, split by '+' gives each key press and the last one is the letter/number/symbal

#     short_last = sorted(shortcuts, key = lambda x: x[0].split("+")[0])
#     short_last = sorted(short_last, key = lambda x: x[0].split("+")[-1])

#     return short_last


def get_sort_key(dict):
    # letter - mod number - whether or not there was shift
    return f"{dict['letter'][0]}m{dict['mod']}s{int(dict['shift'])}"


def get_shortcut(line):

    output = []
    start = len(SHORTCUT_SIGNAL)+1
    current_start = start
    for i, char in enumerate(line[start:]):
        if char in ("+", " "):

            output.append(line[current_start:start+i])
            current_start = start + i + 1

            # end of the shortcut
            if char == " ": break
    
    output.append(line[current_start:])

    return output

def shortcut_to_dict(shortcut, comment=""):
    
    output = dict()
    # get the mod by taking everything after the 4th character (the first 4 will be "$mod")
    mod_number = shortcut[0][len(MOD_SIGNAL):]
    output["mod"] = int(mod_number) if mod_number else 0

    # get the shift
    output["shift"] = shortcut[1].lower() == "shift"
    
    # get the letter, always the second to last entry in the list
    output["letter"] = shortcut[-2]

    output["comment"] = comment

    output["sort_key"] = get_sort_key(output)

    # print(output)
    return output


def convert_to_dictionaries(file_lines):

    short_cuts = []

    for i, line in enumerate(file_lines):
        # found a line with a shortcut
        if line[:len(SHORTCUT_SIGNAL)] == SHORTCUT_SIGNAL:

            short_cut = get_shortcut(line)

            # try to get a comment on this this line, excluding the '\n'
            # at the end of the line
            if COMMENT_SIGNAL in line: # then there is a comment on this line
                comment = line[line.index(COMMENT_SIGNAL):-1]
            elif i > 0 and file_lines[i-1][0] == COMMENT_SIGNAL: # comment is on the above line
                comment = file_lines[i-1][1:-1]
            else:
                comment = short_cut[-1][:-1] # otherwise, just take the code

            short_cuts.append(shortcut_to_dict(short_cut, comment))
        
    return short_cuts


def output_shortcuts(sorted_output, config_file):

        hashes_long = "#"*50
        print(hashes_long)
        print("# Shortcut file for i3")
        print(f"# Config File Used: {config_file}")
        print("# Author: Tony Terrasa")
        print(hashes_long)
        print("\n"*2)
        
        # for tracking when you change letters
        current_letter = sorted_output[0]["letter"]

        # write the file
        for shortcut in sorted_output:

            # put a space each time you transition between two letters
            if shortcut["letter"] != current_letter:
                current_letter = shortcut["letter"]
                print("")
                print(hashes_long)
                print(f"# {shortcut['letter']}")
                print(hashes_long)
        
            # writing each line
            print(f"mod{shortcut['mod'] : <4}{'shift' if shortcut['shift'] else '': <8}{shortcut['letter']: <8}{shortcut['comment']}") 
    


if __name__ == "__main__":

    # default to the default location for the i3 config
    if len(sys.argv) < 2:
        home = str(Path.home())
        default = f"{home}/.config/i3/config"
        config_filename = input(f"No file given, please enter a filenme (default {default}: ")
        config_filename = config_filename if config_filename else default

    else:
        config_filename = sys.argv[1]

    # read file into a list where each entry is a line
    with open(config_filename, "r") as f:
        file_lines = f.readlines()

    dictionary_outputs = convert_to_dictionaries(file_lines)
    sorted_output = sorted(dictionary_outputs, key=lambda x:x["sort_key"])

    output_shortcuts(sorted_output, config_filename)

    # print("\n\nprinting sorted \n\n")
    # for o in sorted_output: print(o)



