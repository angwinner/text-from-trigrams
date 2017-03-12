TEST_PATH = '/home/awinner/Code/day3/trigrams/tests'
SHERLOCK_SMALLER_DICT = {' ': ('One',),
                         ' One': ('night',),
                         'One night': ('--',),
                         'night --': ('it',),
                         '-- it': ('was',),
                         'it was': ('on',),
                         'was on': ('the',),
                         'on the': ('twentieth',),
                         'the twentieth': ('of',),
                         'twentieth of': ('March',),
                         'of March': (',',),
                         'March ,': ('1888',),
                         ', 1888': ('--',),
                         '1888 --': ('I',),
                         '-- I': ('was',),
                         'I was': ('returning',),
                         'was returning': ('from',),
                         'returning from': ('a',),
                         'from a': ('journey',),
                         'a journey': ('to',),
                         'journey to': ('a',),
                         'to a': ('patient',),
                         'a patient': ('(',),
                         'patient (': ('for',),
                         '( for': ('I',),
                         'for I': ('had',),
                         'I had': ('now',),
                         'had now': ('returned',),
                         'now returned': ('to',),
                         'returned to': ('civil',),
                         'to civil': ('practice',),
                         'civil practice': (')',),
                         'practice )': (',',),
                         ') ,': ('when',),
                         ', when': ('my',),
                         'when my': ('way',),
                         'my way': ('led',),
                         'way led': ('me',),
                         'led me': ('through',),
                         'me through': ('Baker',),
                         'through Baker': ('Street',),
                         'Baker Street': ('.',)
                         }


TWINKLE_DICT = {' ': ('Twinkle',),
                ' Twinkle': (',',),
                'Twinkle ,': ('twinkle', 'twinkle'),
                ', twinkle': ('little', 'little'),
                'twinkle little': ('star', 'fish'),
                'little star': ('.',),
                'star .': ('How',),
                '. How': ('I', 'I'),
                'How I': ('wonder', 'wonder'),
                'I wonder': ('what', 'what'),
                'wonder what': ('you', 'you'),
                'what you': ('are', 'wish'),
                'you are': ('.',),
                'are .': ('Up',),
                '. Up': ('above',),
                'Up above': ('the',),
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
                'sky .': ('Twinkle',),
                '. Twinkle': (',',),
                'little fish': ('.',),
                'fish .': ('How',),
                'you wish': ('.',)
                }


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
    assert parse_source(source_path) == {"not real": ("data")}


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
                   '" "': ('Surely',),
                   '" Surely': ('you',),
                   'Surely you': ('jest',),
                   'you jest': ('!',),
                   'jest !': ('"',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('!', '"')


def test_internal_apostrophe():
    from trigrams import parse_line
    source_line = "Surely you're joking!\n"
    trigram_dict = {}
    last_two = ('die', '!')

    result_dict = {'die !': ('Surely',),
                   '! Surely': ("you're",),
                   "Surely you're": ('joking',),
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
                   'was that': ("#(%(*#!@?",)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('that', '#(%(*#!@?')


def test_plural_possessive():
    from trigrams import parse_line
    source_line = "The dogs' kennel stinks.\n"
    trigram_dict = {}
    last_two = ('pets', '.')

    result_dict = {'pets .': ('The',),
                   '. The': ("dogs'",),
                   "The dogs'": ('kennel',),
                   "dogs' kennel": ('stinks',),
                   'kennel stinks': ('.',)
                   }

    (trigram_dict, last_two) = parse_line(source_line, trigram_dict, last_two)
    assert trigram_dict == result_dict
    assert last_two == ('stinks', '.')


def test_file_no_header():
    from trigrams import parse_source
    source_path = TEST_PATH + "/sherlock_smaller.txt"
    assert parse_source(source_path) == SHERLOCK_SMALLER_DICT


def test_file_header():
    # also tests blank lines
    from trigrams import parse_source
    source_path = TEST_PATH + "/sherlock_header.txt"
    assert parse_source(source_path) == SHERLOCK_SMALLER_DICT


def test_build_branches():
    # this test file has dict keys mapped to both 1-tuples and 2-tuples
    from trigrams import parse_source
    source_path = TEST_PATH + "/twinkle.txt"
    assert parse_source(source_path) == TWINKLE_DICT


def test_get_rand_key():
    from trigrams import get_rand_key
    key = get_rand_key(SHERLOCK_SMALLER_DICT)
    keys = SHERLOCK_SMALLER_DICT.keys()
    assert key in keys


def test_get_last_part_key():
    from trigrams import get_last_part_key
    last_part = get_last_part_key('lemon squash')
    assert last_part == 'squash'


def test_get_next_key_there():
    from trigrams import get_next_key
    key = get_next_key(SHERLOCK_SMALLER_DICT, 'a', 'journey')
    assert key == 'a journey'


def test_get_next_key_missing():
    from trigrams import get_next_key
    key = get_next_key(SHERLOCK_SMALLER_DICT, 'green', 'cheese')
    keys = SHERLOCK_SMALLER_DICT.keys()
    assert key in keys
