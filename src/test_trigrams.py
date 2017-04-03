TEST_PATH = '/home/awinner/Code/day3/trigrams/tests'
SHERLOCK_SMALLER_DICT = {' ': ('one',),
                         ' one': ('night',),
                         'one night': (u'\u2014',),
                         'night ' + u'\u2014': ('it',),
                         u'\u2014' + ' it': ('was',),
                         'it was': ('on',),
                         'was on': ('the',),
                         'on the': ('twentieth',),
                         'the twentieth': ('of',),
                         'twentieth of': ('march',),
                         'of march': (',',),
                         'march ,': ('1888',),
                         ', 1888': (u'\u2014',),
                         '1888 ' + u'\u2014': ('i',),
                         u'\u2014' + ' i': ('was',),
                         'i was': ('returning',),
                         'was returning': ('from',),
                         'returning from': ('a',),
                         'from a': ('journey',),
                         'a journey': ('to',),
                         'journey to': ('a',),
                         'to a': ('patient',),
                         'a patient': ('(',),
                         'patient (': ('for',),
                         '( for': ('i',),
                         'for i': ('had',),
                         'i had': ('now',),
                         'had now': ('returned',),
                         'now returned': ('to',),
                         'returned to': ('civil',),
                         'to civil': ('practice',),
                         'civil practice': (',',),
                         'practice ,': ('when',),
                         ', when': ('my',),
                         'when my': ('way',),
                         'my way': ('led',),
                         'way led': ('me',),
                         'led me': ('through',),
                         'me through': ('baker',),
                         'through baker': ('street',),
                         'baker street': ('.',)
                         }


TWINKLE_DICT = {' ': ('twinkle',),
                ' twinkle': (',',),
                'twinkle ,': ('twinkle', 'twinkle'),
                ', twinkle': ('little', 'little'),
                'twinkle little': ('star', 'fish'),
                'little star': ('.',),
                'star .': ('how',),
                '. how': ('i', 'i'),
                'how i': ('wonder', 'wonder'),
                'i wonder': ('what', 'what'),
                'wonder what': ('you', 'you'),
                'what you': ('are', 'wish'),
                'you are': ('.',),
                'are .': ('up',),
                '. up': ('above',),
                'up above': ('the',),
                'above the': ('world',),
                'the world': ('so',),
                'world so': ('high',),
                'so high': (',',),
                'high ,': ('like',),
                ', like': ('a',),
                'like a': ('diamond',),
                'a diamond': ('in',),
                'diamond in': ('the',),
                'in the': ('sky',),
                'the sky': ('.',),
                'sky .': ('twinkle',),
                '. twinkle': (',',),
                'little fish': ('.',),
                'fish .': ('how',),
                'you wish': ('.',)
                }

TOO_MUCH_PUNCTUATION_DICT = {'green eggs': ('.',),
                             'and ham': ('.',),
                             'Sam i': ('.',),
                             'will not': ('.',),
                             'eat it': ('.',),
                             'in a': ('.',),
                             'boat .': ('i',)
                             }

SHERLOCK_SMALL_NAMES = ['March', 'I', 'Baker', 'Street', 'Study', 'Scarlet',
                        'Holmes']

SHERLOCK_ALT_SMALL_NAMES = ['Holmes', 'Doctor', 'Boswell']

SOURCE_META_SHERLOCK_SMALL = {'proper_names': SHERLOCK_SMALL_NAMES,
                              'quotes': [],
                              'parens': ['w8'],
                              'brackets': []}

SOURCE_META_SHERLOCK_ALT_SMALL = {'proper_names': SHERLOCK_ALT_SMALL_NAMES,
                                  'quotes': ['s1', 's5', 'w3', 's4', 's1'],
                                  'parens': [],
                                  'brackets': ['s1', 'w3']}


def test_parse_source_notpath():
    from trigrams import parse_source
    source_path = "/usr/usr/usr"
    assert parse_source(source_path) == 1


def test_parse_source_notfile():
    from trigrams import parse_source
    source_path = "/usr/bin"
    assert parse_source(source_path) == 2


def test_open_source():
    from trigrams import parse_source
    source_path = TEST_PATH + "/dundertest.txt"
    trigram_dict, source_meta = parse_source(source_path)
    assert trigram_dict == {"not real": ("data")}


def test_parse_word_alnum():
    from trigrams import parse_word
    assert parse_word('cat') == ['cat']


def test_parse_word_solo():
    from trigrams import parse_word
    assert parse_word('&') == ['&']


def test_parse_word_solo_hyphen():
    from trigrams import parse_word
    assert parse_word('-') == [u'\u2014']


def test_parse_word_end_hyphen():
    from trigrams import parse_word
    assert parse_word('half-') == ['half-']


def test_parse_word_full_enclosed():
    from trigrams import parse_word
    assert parse_word('(only)') == ['(only)']
    assert parse_word('"scare"') == ['"scare"']


def test_parse_word_front_enclosed():
    from trigrams import parse_word
    assert parse_word('(Only') == ['(', 'only']
    assert parse_word('"Only') == ['"', 'only']


def test_parse_word_end_enclosed():
    from trigrams import parse_word
    assert parse_word('said]') == ['said']
    assert parse_word('said"') == ['said']


def test_parse_word_end_punc():
    from trigrams import parse_word
    assert parse_word('said.') == ['said', '.']
    assert parse_word('said...') == ['said', '...']


def test_parse_word_multi_end_punc():
    from trigrams import parse_word
    assert parse_word('said!"') == ['said', '!']
    assert parse_word('said!!!') == ['said', '!', '!', '!']
    assert parse_word('said!")') == ['said', '!']


def test_parse_word_multi_front_punc():
    from trigrams import parse_word
    assert parse_word('("Every') == ['(', '"', 'every']


def test_parse_word_ellipsis():
    from trigrams import parse_word
    assert parse_word('...') == ['...']
    assert parse_word('continued...') == ['continued', '...']
    assert parse_word('ah...choo') == ['ah...choo']


def test_parse_word_em_dash():
    from trigrams import parse_word
    assert parse_word('should--but') == ['should', u'\u2014', 'but']
    assert parse_word('--') == [u'\u2014']


def test_parse_line():
    from trigrams import parse_line
    # byte_line = b'__test__\n'
    # source_line = byte_line.decode('utf-8')
    source_line = '__test__\n'
    trigram_dict = {}
    last_two = ('', '')
    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == {"not real": ("data")}
    assert last_two == ('fake', 'fake')


def test_short_line_no_punc():
    from trigrams import parse_line
    source_line = 'Chapter 1\n'
    trigram_dict = {}
    last_two = ('no', 'punctuation')
    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == {}
    assert last_two == ('', '')


def test_short_line_punc():
    from trigrams import parse_line
    source_line = 'and he died.\n'
    trigram_dict = {}
    last_two = ('he', 'fell')

    result_dict = {'he fell': ('and',),
                   'fell and': ('he',),
                   'and he': ('died',),
                   'he died': ('.',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('died', '.')


def test_quotes_begin_end():
    from trigrams import parse_line
    source_line = '''"Surely you jest!"\n'''
    trigram_dict = {}
    last_two = ('.', '"')

    result_dict = {'. "': ('"',),
                   '" "': ('surely',),
                   '" surely': ('you',),
                   'surely you': ('jest',),
                   'you jest': ('!',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('jest', '!')


def test_internal_apostrophe():
    from trigrams import parse_line
    source_line = "Surely you're joking!\n"
    trigram_dict = {}
    last_two = ('die', '!')

    result_dict = {'die !': ('surely',),
                   '! surely': ("you're",),
                   "surely you're": ('joking',),
                   "you're joking": ('!',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('joking', '!')


def test_curse_string_middle():
    from trigrams import parse_line
    source_line = "that #(%(*#!@ idiot!\n"
    trigram_dict = {}
    last_two = ('who', 'was')

    result_dict = {'who was': ('that',),
                   'was that': ("#(%(*#!@",),
                   "that #(%(*#!@": ('idiot',),
                   "#(%(*#!@ idiot": ('!',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('idiot', '!')


def test_curse_string_end():
    from trigrams import parse_line
    source_line = "that #(%(*#!@?\n"
    trigram_dict = {}
    last_two = ('who', 'was')

    result_dict = {'who was': ('that',),
                   'was that': ("#(%(*#!@",),
                   'that #(%(*#!@': ('?',),
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('#(%(*#!@', '?')


def test_plural_possessive():
    from trigrams import parse_line
    source_line = "The dogs' kennel stinks.\n"
    trigram_dict = {}
    last_two = ('pets', '.')

    result_dict = {'pets .': ('the',),
                   '. the': ("dogs'",),
                   "the dogs'": ('kennel',),
                   "dogs' kennel": ('stinks',),
                   'kennel stinks': ('.',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('stinks', '.')


def test_file_no_header():
    from trigrams import parse_source
    source_path = TEST_PATH + "/sherlock_smaller.txt"
    trigram_dict, source_meta = parse_source(source_path)
    assert trigram_dict == SHERLOCK_SMALLER_DICT


def test_file_header():
    # also tests blank lines
    from trigrams import parse_source
    source_path = TEST_PATH + "/sherlock_header.txt"
    trigram_dict, source_meta = parse_source(source_path)
    assert trigram_dict == SHERLOCK_SMALLER_DICT


def test_build_branches():
    # this test file has dict keys mapped to both 1-tuples and 2-tuples
    from trigrams import parse_source
    source_path = TEST_PATH + "/twinkle.txt"
    trigram_dict, source_meta = parse_source(source_path)
    assert trigram_dict == TWINKLE_DICT


def test_build_list_proper():
    from trigrams import build_lists
    import io
    source_path = TEST_PATH + "/sherlock_small.txt"
    f = io.open(source_path, encoding='utf-8')
    proper_names, quotes, parens, brackets = build_lists(f)
    f.close()
    assert set(proper_names) == set(SHERLOCK_SMALL_NAMES)


def test_build_list_parens():
    from trigrams import build_lists
    import io
    source_path = TEST_PATH + "/sherlock_small.txt"
    f = io.open(source_path, encoding='utf-8')
    proper_names, quotes, parens, brackets = build_lists(f)
    f.close()
    assert set(parens) == set(['w8'])


def test_build_list_quotes():
    from trigrams import build_lists
    import io
    source_path = TEST_PATH + "/sherlock_alt_small.txt"
    f = io.open(source_path, encoding='utf-8')
    proper_names, quotes, parens, brackets = build_lists(f)
    f.close()
    assert set(quotes) == set(['s1', 's5', 'w3', 's4', 's1'])
    # sets ignore duplicates, so also check
    assert len(quotes) == 5


def test_build_list_brackets():
    from trigrams import build_lists
    import io
    source_path = TEST_PATH + "/sherlock_alt_small.txt"
    f = io.open(source_path, encoding='utf-8')
    proper_names, quotes, parens, brackets = build_lists(f)
    f.close()
    assert set(brackets) == set(['s1', 'w3'])


def test_get_rand_key():
    from trigrams import get_rand_key
    key = get_rand_key(SHERLOCK_SMALLER_DICT)
    keys = SHERLOCK_SMALLER_DICT.keys()
    assert key in keys


def test_get_key_exists():
    from trigrams import get_key
    key, was_rand = get_key(SHERLOCK_SMALLER_DICT, 'a', 'journey')
    assert key == 'a journey'
    assert not was_rand


def test_get_key_missing():
    from trigrams import get_key
    key, was_rand = get_key(SHERLOCK_SMALLER_DICT, 'green', 'cheese')
    keys = SHERLOCK_SMALLER_DICT.keys()
    assert key in keys
    assert was_rand


def test_punc_after_punc():
    from trigrams import get_next_word
    word1, word2 = get_next_word(TOO_MUCH_PUNCTUATION_DICT, 'not', '!')
    assert word2 == 'i'


def test_format_word_nls_no():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    state['in_s'] = True
    next_word, state = format_word('hop', 'hop', state)
    assert next_word == ' hop'


def test_format_word_nls_yes():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    next_word, state = format_word('hop', '!', state)
    assert next_word == '!'


def test_format_word_out_sentc_alpha():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    next_word, state = format_word("", 'apple', state)
    assert next_word == ' Apple'
    assert state['in_s']


def test_format_word_out_sentc_num():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    next_word, state = format_word("", '18', state)
    assert next_word == ' 18'
    assert not state['in_s']


def test_format_word_in_sentc_alpha():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    state['in_s'] = True
    next_word, state = format_word("", 'apple', state)
    assert next_word == ' apple'
    assert state['in_s']
    # in/out sentc, next_word alpha/not, in SENTC_END, next_word comma


def test_format_word_in_sentc_end():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    state['in_s'] = True
    next_word, state = format_word('frog', '.', state)
    assert next_word == '.'
    assert not state['in_s']


def test_format_word_out_sentc_end():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    state['in_s'] = False
    next_word, state = format_word('frog', '.', state)
    assert next_word == '.'
    assert not state['in_s']


def test_format_word_start_quote():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    next_word, state = format_word('frog', '"', state)
    assert next_word == ' "'
    assert state['in_q']


def test_format_word_extra_quote():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    state['in_q'] = True
    next_word, state = format_word('frog', '"', state)
    assert next_word == ''
    assert state['in_q']


def test_format_word_start_parens():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    next_word, state = format_word('frog', '(', state)
    assert next_word == ' ('
    assert state['in_p']


def test_format_word_start_brackets():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    next_word, state = format_word('frog', '[', state)
    assert next_word == ' ['
    assert state['in_b']


def test_format_word_em_dash():
    from trigrams import format_word, initialize_state
    state = initialize_state()
    state['in_s'] = True
    next_word, state = format_word(u'\u2014', 'really', state)
    assert next_word == 'really'

def test_check_state_changes():
    from trigrams import check_state_changes, initialize_state
    old_state = initialize_state()
    state = initialize_state()
    old_state['in_s'] = True
    state['in_p'] = True
    state['in_b'] = True
    state['in_q'] = True
    results = check_state_changes(old_state, state)
    assert 'end sentc' in results
    assert 'start quote' in results
    assert 'start parens' in results
    assert 'start brackets' in results


def test_update_state_end_sentc_no_q():
    from trigrams import update_state, initialize_state
    old_state = initialize_state()
    state = initialize_state()
    old_state['in_s'] = True
    state['in_s'] = False
    frmt_word = ''
    source_meta = {}
    also_print, state = update_state(old_state, state, frmt_word, source_meta)
    assert also_print == ''
    assert state['q_sentc_count'] == 0


def test_update_state_end_sentc_yes_q():
    from trigrams import update_state, initialize_state
    old_state = initialize_state()
    state = initialize_state()
    old_state['in_s'] = True
    state['in_s'] = False
    old_state['in_q'] = True
    state['in_q'] = True
    frmt_word = 'yesq'
    source_meta = {}
    also_print, state = update_state(old_state, state, frmt_word, source_meta)
    assert also_print == ''
    assert state['q_sentc_count'] == 1


def test_update_state_start_quote():
    from trigrams import update_state, initialize_state
    old_state = initialize_state()
    state = initialize_state()
    old_state['in_q'] = False
    state['in_q'] = True
    frmt_word = ''
    source_meta = {'proper_names': [],
                   'quotes': ['s3'],
                   'parens': ['w8'],
                   'brackets': []}
    also_print, state = update_state(old_state, state, frmt_word, source_meta)
    assert also_print == ''
    assert state['q_goal'] == 's3'


def test_update_state_space():
    from trigrams import update_state, initialize_state
    old_state = initialize_state()
    state = initialize_state()
    old_state['in_q'] = True
    old_state['in_p'] = True
    old_state['in_b'] = True
    state['in_q'] = True
    state['in_p'] = True
    state['in_b'] = True
    frmt_word = ' dog'
    source_meta = {'proper_names': [],
                   'quotes': ['s3'],
                   'parens': ['w8'],
                   'brackets': []}
    also_print, state = update_state(old_state, state, frmt_word, source_meta)
    assert also_print == ''
    assert state['q_word_count'] == 1
    assert state['p_word_count'] == 1
    assert state['b_word_count'] == 1


def test_update_state_check_goal_words():
    from trigrams import update_state, initialize_state
    old_state = initialize_state()
    state = initialize_state()
    state['q_goal'] = 'w5'
    state['p_goal'] = 'w6'
    state['b_goal'] = 'w7'
    state['q_word_count'] = 5
    state['p_word_count'] = 6
    state['b_word_count'] = 7
    frmt_word = ' dog'
    source_meta = {'proper_names': [],
                   'quotes': ['s3'],
                   'parens': ['w8'],
                   'brackets': []}
    also_print, state = update_state(old_state, state, frmt_word, source_meta)
    assert also_print == '")]'
    assert state['q_word_count'] == 0
    assert state['q_sentc_count'] == 0
    assert state['q_goal'] == ''
    assert not state['in_q']
    assert state['p_word_count'] == 0
    assert state['p_sentc_count'] == 0
    assert state['p_goal'] == ''
    assert not state['in_p']
    assert state['b_word_count'] == 0
    assert state['b_sentc_count'] == 0
    assert state['b_goal'] == ''
    assert not state['in_b']
