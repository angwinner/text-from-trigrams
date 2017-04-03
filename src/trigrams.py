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
    source_meta = {'proper_names': proper_names,
                   'quotes': quotes,
                   'parens': parens,
                   'brackets': brackets}
    f.close()

    return trigram_dict, source_meta


def get_rand_key(trigram_dict):
    key_index = random.randrange(len(trigram_dict))
    key_list = list(trigram_dict.keys())
    return key_list[key_index]


def get_key(trigram_dict, word1, word2):
    key = word1 + ' ' + word2
    if key in trigram_dict:
        return key, False
    else:
        return get_rand_key(trigram_dict), True


def get_next_word(trigram_dict, word1, word2):
    key, was_rand = get_key(trigram_dict, word1, word2)

    choices = tuple(trigram_dict[key])
    if len(choices) == 1:
        next_word = str(choices[0])
    else:
        choice_index = random.randrange(len(choices))
        next_word = str(choices[choice_index])

    # don't follow punctuation with punctuation
    while not word2.isalpha() and was_rand and not next_word.isalpha():
        ignore, next_word = get_next_word(trigram_dict, word1, word2)

    return word2, next_word


def initialize_state():
    # in_sentence, in_quote, in_parentheses, in_brackets
    state = {'in_s': False, 'in_q': False, 'in_p': False, 'in_b': False,
             'q_sentc_count': 0, 'q_word_count': 0, 'q_goal': '',
             'p_sentc_count': 0, 'p_word_count': 0, 'p_goal': '',
             'b_sentc_count': 0, 'b_word_count': 0, 'b_goal': ''}
    return state


def check_state_changes(old_state, state):
    changes = []
    if old_state['in_s'] and not state['in_s']:
        changes.append('end sentc')
    if not old_state['in_q'] and state['in_q']:
        changes.append('start quote')
    if not old_state['in_p'] and state['in_p']:
        changes.append('start parens')
    if not old_state['in_b'] and state['in_b']:
        changes.append('start brackets')
    return changes


def update_state(old_state, state, formatted_word, source_meta):
    also_print = ''
    state_changes = check_state_changes(old_state, state)
    for change in state_changes:
        if change == 'end sentc':
            if state['in_q']:
                state['q_sentc_count'] += 1
            if state['in_p']:
                state['p_sentc_count'] += 1
            if state['in_b']:
                state['b_sentc_count'] += 1
        if change == 'start quote':
            state['q_goal'] = get_quote_length(source_meta)
        if change == 'start parens':
            state['p_goal'] = get_parens_length(source_meta)
        if change == 'start brackets':
            state['b_goal'] = get_brackets_length(source_meta)

    if formatted_word.startswith(' '):  # these counts are space-delimited
        if state['in_q']:
            state['q_word_count'] += 1
        if state['in_p']:
            state['p_word_count'] += 1
        if state['in_b']:
            state['b_word_count'] += 1

    # see if q, p, b counts equal goals
    q_goal = state['q_goal']
    if not q_goal == '':
        if q_goal.startswith('s'):
            if (int(state['q_sentc_count']) >= int(q_goal.lstrip('s'))):
                also_print += '"'
                state = reset_quote(state)
        if q_goal.startswith('w'):
            if int(state['q_word_count']) >= int(q_goal.lstrip('w')):
                also_print += '"'
                state = reset_quote(state)
    p_goal = state['p_goal']
    if not p_goal == '':
        if p_goal.startswith('s'):
            if (int(state['p_sentc_count']) >= int(p_goal.lstrip('s'))):
                also_print += ')'
                state = reset_parens(state)
        if p_goal.startswith('w'):
            if int(state['p_word_count']) >= int(p_goal.lstrip('w')):
                also_print += ')'
                state = reset_parens(state)
    b_goal = state['b_goal']
    if not b_goal == '':
        if b_goal.startswith('s'):
            if (int(state['b_sentc_count']) >= int(b_goal.lstrip('s'))):
                also_print += ']'
                state = reset_brackets(state)
        if b_goal.startswith('w'):
            if int(state['b_word_count']) >= int(b_goal.lstrip('w')):
                also_print += ']'
                state = reset_brackets(state)

    return also_print, state


def reset_quote(state):
    state['q_goal'] = ''
    state['in_q'] = False
    state['q_word_count'] = 0
    state['q_sentc_count'] = 0
    return state


def reset_parens(state):
    state['p_goal'] = ''
    state['in_p'] = False
    state['p_word_count'] = 0
    state['p_sentc_count'] = 0
    return state


def reset_brackets(state):
    state['b_goal'] = ''
    state['in_b'] = False
    state['b_word_count'] = 0
    state['b_sentc_count'] = 0
    return state


def get_quote_length(source_meta):
    quotes = source_meta['quotes']
    i = random.randrange(len(quotes))
    return quotes[i]


def get_parens_length(source_meta):
    parens = source_meta['parens']
    i = random.randrange(len(parens))
    return parens[i]


def get_brackets_length(source_meta):
    brackets = source_meta['brackets']
    i = random.randrange(len(brackets))
    return brackets[i]


def format_word(prev_word, next_word, state, source_meta):
    # 'format' means add a space (or not) to the left of next_word
    # and capitalize it as necessary
    no_left_space = ['.', ',', ':', ';', '!', '?', '-']
    nls_flag = False
    if next_word in no_left_space:
        nls_flag = True

    if not state['in_s'] and next_word[0].isalpha():
        state['in_s'] = True
        if not next_word.isupper():  # don't de-capitalize all caps
            next_word = next_word.capitalize()
    if next_word in SENTENCE_END:
        state['in_s'] = False

    if not state['in_q'] and next_word == '"':
        state['in_q'] = True
    elif state['in_q'] and next_word == '"':
        # we've hit a new quote before finishing our old one -- erase it
        next_word = ''
        nls_flag = True

    if not state['in_p'] and next_word == '(':
        state['in_p'] = True
    if not state['in_b'] and next_word == '[':
        state['in_b'] = True

    # if next_word in #proper names
    proper_names = source_meta['proper_names']
    if next_word in proper_names:
        if not next_word.isupper():  # don't de-capitalize all caps
            next_word = next_word.capitalize()

    if prev_word == u'\u2014':
        nls_flag = True

    if not nls_flag:
        next_word = ' ' + next_word

    return next_word, state


def write_story(trigram_dict, source_meta, out_length):
    word1 = ''
    word2 = ''

    state = initialize_state()

    for i in range(out_length):
        prev_word, next_word = get_next_word(trigram_dict, word1, word2)
        old_state = state
        formatted_word, state = format_word(prev_word, next_word,
                                            state, source_meta)
        print(formatted_word, end='')
        word1 = prev_word
        word2 = next_word

        also_print, state = update_state(old_state, state, formatted_word,
                                         source_meta)
        print(also_print, end='')

    print('\n')


def story_from_source(source_path, out_length):
    trigram_dict, source_meta = parse_source(source_path)
    write_story(trigram_dict, source_meta, out_length)


def main():
    if len(sys.argv) != 3:
        print(USAGE)
        sys.exit(1)

    story_from_source(sys.argv[1], int(sys.argv[2]))
    sys.exit(0)


if __name__ == '__main__':
    main()
