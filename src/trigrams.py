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

ENDING_PUNC = ['.', '?', '!', ':', ';', ',']  # ellipsis exluded
SENTENCE_END = ['.', '?', '!']
ENCLOSING_PUNC = ['"', '(', ')', '[', ']']


def add_trigram(trigram_dict, key, value):
    if key in trigram_dict:
        vals = trigram_dict[key]
        vals = vals + (value,)
        trigram_dict[key] = vals
    else:
        trigram_dict[key] = (value,)
    return trigram_dict


def strip_punc(pre_p, word, post_p):

    done_flag = False

    # Endquotes, end parens, end brackets are not placed via trigram.
    # Words with paired enclosing punc are kept as-is, ie. dog(s), (S)he,
    # (eventually), and "scary" scare quotes
    if word[-1] == ')':
        if '(' not in word:
            word = word.rstrip(')')
        else:
            done_flag = True
    if word[-1] == ']':
        if '[' not in word:
            word = word.rstrip(']')
        else:
            done_flag = True
    if word[-1] == '"':
        if word.startswith('"'):
            done_flag = True
        else:
            word = word.rstrip('"')

    if not done_flag:
        if word[0] in ENCLOSING_PUNC:
            pre_p.append(word[0])
            word = word[1: len(word)]

    if word.endswith('...'):
        post_p.insert(0, '...')
        word = word[0: len(word) - 3]

    if word[-1] in ENDING_PUNC:
        post_p.insert(0, word[-1])
        word = word[0: -1]

    if not done_flag and len(word) > 0:
        if (word[-1] in ENCLOSING_PUNC or
            word[-1] in ENDING_PUNC or
            word[0] in ENCLOSING_PUNC):

            (pre_p, word, post_p) = strip_punc(pre_p, word, post_p)

    return (pre_p, word, post_p)


def parse_word(word):
    """ Words in this sense are just space-separated blocks of text.
    Punctuation elements are either left in the word or returned as
    independent words. """

    if len(word) == 0:
        return []

    if '--' in word:
        word = word.replace('--', u'\u2014')

    if word == '-':  # only replace hyphens surrounded by spaces
        word = u'\u2014'

    solo_punc = ['&', u'\u2014', '...']
    if word in solo_punc:
        return [word]

    pre_punc = []
    post_punc = []

    if not word.isalnum():
        pre_punc, word, post_punc = strip_punc(pre_punc, word, post_punc)

    # dict entries will be recapitalized via proper name recognition
    # or start sentence rules as required
    firstletter = word[0]
    if firstletter.isupper():
        word = firstletter.lower() + word[1:len(word)]

    result = [word]
    # parse central punctuation like mother-in-law, his/hers, ah...choo!,
    # Ben's or em dash [it was over--I knew] Only em dash is its own word
    if u"\u2014" in word:
        emdashed = word.split(u"\u2014")
        word1parsed = parse_word(emdashed[0])
        word2parsed = parse_word(emdashed[1])
        result = word1parsed + [u'\u2014'] + word2parsed

    return pre_punc + result + post_punc


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


def build_lists(f):
    proper_names = []
    quotes = []  # s1, w22 - how many words/sentences each quote spanned
    parens = []
    brackets = []

    in_sentc = False
    proper = ''
    accumulating_proper = False
    in_quote = False
    q_word_count = 0
    q_sentc_count = 0
    in_parens = False  # doesn't deal with nested parens or brackets
    p_word_count = 0
    p_sentc_count = 0
    in_brackets = False
    b_word_count = 0
    b_sentc_count = 0

    for line in f:

        if len(line) > 0:
            for i in range(0, len(line)):
                char = line[i]
                if char.isupper():
                    if not in_sentc:
                        in_sentc = True
                    else:
                        proper += char
                        accumulating_proper = True
                elif char.isspace() or char == '\n':
                    if accumulating_proper:
                        stripped = strip_punc([], proper, [])
                        proper = stripped[1]
                        if proper not in proper_names:
                            proper_names.append(proper)
                        accumulating_proper = False
                        proper = ''
                    if in_quote:
                        q_word_count += 1
                    if in_parens:
                        p_word_count += 1
                    if in_brackets:
                        b_word_count += 1
                elif char in SENTENCE_END:
                    in_sentc = False
                    if in_quote:
                        q_sentc_count += 1
                    if in_parens:
                        p_sentc_count += 1
                    if in_brackets:
                        b_sentc_count += 1
                elif char == '"':
                    if in_quote:
                        in_quote = False
                        if q_word_count > 0:  # if not, in trigrams with quotes
                            # save to quote list
                            if q_sentc_count > 0:
                                quotes.append(('s' + str(q_sentc_count)))
                            else:
                                quotes.append(('w' + str(q_word_count + 1)))
                        q_word_count = 0
                        q_sentc_count = 0
                    else:
                        in_quote = True
                elif char == '(':
                    in_parens = True
                elif char == ')':
                    in_parens = False
                    if p_word_count > 0:
                        if p_sentc_count > 0:
                            parens.append(('s' + str(p_sentc_count)))
                        else:
                            parens.append(('w' + str(p_word_count + 1)))
                    p_word_count = 0
                    p_sentc_count = 0
                elif char == '[':
                    in_brackets = True
                elif char == ']':
                    in_brackets = False
                    if b_word_count > 0:
                        if b_sentc_count > 0:
                            brackets.append(('s' + str(b_sentc_count)))
                        else:
                            brackets.append(('w' + str(b_word_count + 1)))
                    b_word_count = 0
                    b_sentc_count = 0
                else:
                    if accumulating_proper:
                        proper += char

        else:
            # an empty line
            in_sentc = False
            proper = ''
            accumulating_proper = False

    return proper_names, quotes, parens, brackets


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

    # go through source again to gather info can span multiple lines
    f = io.open(source_path, encoding='utf-8')
    proper_names, quotes, parens, brackets = build_lists(f)
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
        # make sure you don't return punc after punc
        # use str.ispunctuation()
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
        # impose capitalization, enclosing punc
        # and appropriate spacing for punc
        print(next_word, end=' ')
        key = get_next_key(trigram_dict, previous_word, next_word)


def story_from_source(source_path, out_length):
    trigram_dict = parse_source(source_path)
    write_story(trigram_dict, out_length)


def main():
    if len(sys.argv) != 3:
        print(USAGE)
        sys.exit(1)

    story_from_source(sys.argv[1], int(sys.argv[2]))
    sys.exit(0)
