from __future__ import print_function
import pathlib
import io
import random
import sys

USAGE = """
Usage: trigrams sourcefile length

    where sourcefile points to a text file and length is the length of
    the desired output

"""


def add_trigram(trigram_dict, key, value):
    if key in trigram_dict:
        vals = trigram_dict[key]
        vals = vals + (value,)
        trigram_dict[key] = vals
    else:
        trigram_dict[key] = (value,)
    return trigram_dict


def parse_word(word):
    
    punc_words = []
    if word.isalnum():
        punc_words.append(word)
    else:
        if '--' in word:
            mdash_words = word.split('--')
            if len(mdash_words) = 3: # if not, do nothing, use as-is
                punc_words = parse_word(mdash_words[0])
                punc_words.append('--')
                word = mdash_words[1]

        # this isn't spanish, assume the only prefixes are " (
        if word.startswith('"'):
            punc_words.append('"')
            word = word.lstrip('"')
        if word.startswith('('):
            punc_words.append('(')
            word = word.lstrip('(')
        end_punc_reversed = []
        if word.endswith('"'):
            end_punc_reversed.append('"')
            word = word.rstrip('"')
        if len(word) > 0:
            if word[0].isalnum():
                if not word.endswith("'"):  # i.e. this is my dogs'
                    #  trim off all punctuation on right as new words
                    length = len(word)
                    for i in range(length):
                        if not word[-1].isalnum():
                            end_punc_reversed.append(word[-1])
                            word = word.rstrip(word[-1])
                    punc_words.append(word)
                else:  # this is my dogs'
                    punc_words.append(word)
            else:  # maybe this is #^%&*%!
                punc_words.append(word)

        end_punc_reversed.reverse()
        punc_words = punc_words + end_punc_reversed

    return punc_words


def parse_line(line, trigram_dict, last_two):
    if line == '__test__\n':
        return ({"not real": ("data")}, ('fake', 'fake'))

    line = line.rstrip('\n')

    if len(line) == 0:
        return (trigram_dict, ('', ''))

    """ if a line is < 50 chars long and does not end with punctuation,
    we will assume it is a title or other structural element and we will
    ignore it. This will also skip multi-line lists after colons."""
    if len(line) < 50:
        if line[-1] not in '".?!':
            return (trigram_dict, ('', ''))

    # punctuation marks will count as individual 'words'
    spaced_words = line.split(' ')
    all_words = [last_two[0], last_two[1]]
    for word in spaced_words:
        all_words = all_words + parse_word(word)

    for i in range(len(all_words)-2):
        key = all_words[i] + ' ' + all_words[i+1]
        trigram_dict = add_trigram(trigram_dict, key, all_words[i+2])

    new_last_two = (all_words[-2], all_words[-1])

    return (trigram_dict, new_last_two)


def skip_header(f):
    in_header = True
    while in_header:
        line = f.readline()
        if 'Produced by' in line:
            in_header = False


def build_dict(f):
    first_line = f.readline()
    if 'project gutenberg' in first_line.lower():
        skip_header(f)
        first_line = ''
    trigram_dict = {}
    last_two = ('', '')
    (trigram_dict, last_two) = parse_line(first_line, trigram_dict, last_two)

    for line in f:
        (trigram_dict, last_two) = parse_line(line, trigram_dict, last_two)
    return trigram_dict


def parse_source(source_path):
    """ Returns a dict of two-word keys linked to next word options"""

    pth = pathlib.Path(source_path)
    if not pth.exists():
        print("Sorry, I could not find that file.")
        return 1
    if not pth.is_file():
        print("Sorry, that's not a file.")
        # and again, get main to exit
        return 2

    f = io.open(source_path, encoding='utf-8')
    trigram_dict = build_dict(f)
    f.close()

    return trigram_dict


def get_rand_key(trigram_dict):
    key_index = random.randrange(len(trigram_dict))
    key_list = list(trigram_dict.keys())
    return key_list[key_index]


def get_last_part_key(key):
    two_words = key.split(' ')
    return two_words[1]


def get_next_key(trigram_dict, word1, word2):
    key = word1 + ' ' + word2
    if key in trigram_dict:
        return key
    else:
        return get_rand_key(trigram_dict)


def write_story(trigram_dict, out_length):
    key = get_rand_key(trigram_dict)
    previous_word = get_last_part_key(key)
    next_word = ''

    for i in range(out_length):
        choices = tuple(trigram_dict[key])
        if len(choices) == 1:
            next_word = choices[0]
        else:
            choice_index = random.randrange(len(choices))
            next_word = choices[choice_index]
        print(next_word, end=' ')
        key = get_next_key(trigram_dict, previous_word, next_word)


def story_from_source(source_path, out_length):
    trigram_dict = parse_source(source_path)
    write_story(trigram_dict, out_length)


def main():
    if __name__ == '__main__':
        if len(sys.argv) != 2:
            print(USAGE)
            sys.exit(1)

        story_from_source(sys.argv[0], int(sys.argv[1]))
        sys.exit(0)
