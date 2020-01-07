from argparse import ArgumentParser
from string import punctuation
from typing import Tuple, List

punctuation += '—'  # other punctuation to be handled more robustly in future.

###############################  El Saltillo  #################################
#                                                                             #
# This script will make a number of references to the 'saltillo', which in    #
# Classical Nahuatl was a glottal stop, and in many modern varieties in is a  #
# glottal fricative. Change the following constant to change how this phoneme #
# is transcribed.                                                             #
#                                                                             #
saltillo = '?'  # 'h'
###############################################################################

bare_vowels = {"a", "e", "i", "o", "u"}

alveolar_sibilants = {'s', 'ç', 'z'}

ident_vowels = {"a", "e", "i", "o"}

ident_consonants = {"p", "m", "n", "l", "w", "k"}

long2bare_vowels = {'ē': 'e:', 'ō': 'o:', 'ā': 'a:', 'ī': 'i:'}

saltillo2bare_vowels = {'è': 'e', 'ê': 'e', 'ó': 'o', 'ô': 'o',
                        'à': 'a', 'â': 'a', 'î': 'i', 'ì': 'i'}

spanish_ident_vowels = {"á", "é", "í", "ó", "ú"}
spanish_ident_consonants = {'d', 'ñ', 'r'}

all_vowels = (
    bare_vowels
    .union(spanish_ident_vowels)
    .union(set(long2bare_vowels.keys()))
    .union(set(saltillo2bare_vowels.keys()))
)


def map_grapheme_to_phoneme(new_char_idx: int,
                            current_char: str,
                            next_char: str = '',
                            huiptla_char: str = '') -> Tuple[int, List[str]]:
    """
    Maps the current grapheme with its context to a sequence of one-or-more
    phonemes. It is almost always just one phoneme, with the unique exception
    of the saltillo/glottal fricative, since in many orthographies this is
    represented by a single character with a diacritic.

    Parameters
    ----------
    new_char_idx: int
        The index of `current_char` in the master string. This index will
        be incremented according to the rules fired in this function. Most
        rules only increment the index by one, moving on to the next character.
        However, for example if the current and next graphemes are "q" and "u"
        respectively, the phoneme returned will be 'k', and
        `current_char_index` will be incremented by 2.

    current_char: str
        The character at the current index.

    next_char: str
        The character following current. If current char is the last of the
        word, `next_char` is an empty str.

    huiptla_char: str
        The character at index i + 2. 'Huiptla' is the Nahuatl word meaning
        "the day after tomorrow," used here metaphorically as "the character
        after next." If current char is the second-to-last of the word,
        `next_char` is an empty str.

    Returns
    -------

    """
    new_char_idx += 1

    #
    # If the grapheme is a vowel marked with a diacritic eg 'ā' representing
    # length, map it to its bare form plus ':'. If the grapheme is a bare
    # vowel, check if it is followed by the same grapheme. This is one way of
    # denoting long vowels in some orthographies.
    #
    if current_char in long2bare_vowels:
        phonemes = [long2bare_vowels[current_char]]

    elif current_char in ident_vowels:
        if next_char == current_char:  # long vowels
            phonemes = ["{}:".format(current_char)]
            new_char_idx += 1
        else:
            phonemes = [current_char]

    #
    # The graphemes 'k' and 'c' often correspond to the same phonemes in
    # different orthographies.
    #
    # 'c' can combine with 'h' to form /tS/, correspond to /k_w/ when followed
    # by 'u' and a non-'u' vowel. if followed by 'i' or 'e' its corresponding
    # phoneme is /s/. It is /k/ elsewhere.
    #
    # 'k', in the orthographies that use it, always maps to either /k_w/ when
    # followed by 'u' and a non-'u' vowel, or /k/ elsewhere.
    #
    elif current_char in {'k', 'c'}:
        if next_char == 'u' and huiptla_char in {'a', 'i', 'e'}:
            phonemes = ['k_w']
            new_char_idx += 1
        elif next_char == 'h':
            if huiptla_char == 'u':
                phonemes = ['k_w']
                new_char_idx += 2
            else:
                phonemes = ['tS']
                new_char_idx += 1
        elif next_char in {'i', 'e'} and current_char == 'c':
            phonemes = ['s']
        else:
            phonemes = ['k']

    #
    # 'qu' in most well-defined orthographies maps to /k/. However, in some
    # older writings, the sequence 'qua' maps to /k_w a/ as in 'qualli'
    # (in modern SEP writing would be written as 'kuali' or 'kwali').
    #
    elif current_char == 'q':
        if next_char == 'u':
            if huiptla_char == 'a':
                phonemes = ['w']
            else:
                phonemes = ['k']
            new_char_idx += 1
        else:
            phonemes = ['k']

    #
    # 'h+u+V' seems to be universally /w/ + V
    #
    elif ((current_char, next_char) == ('h', 'u')
          and huiptla_char in {"a", "i", "e"}):
        phonemes = ['w']
        new_char_idx += 1

    #
    # The grapheme 'u' maps to /w/ when preceded by 'h', or if followed by an
    # 'h' at the end of the word. Otherwise, treat it as the vowel /u/.
    #
    elif current_char == 'u':
        if next_char == 'h' and not huiptla_char:
            phonemes = ['w']
            new_char_idx += 1
        elif next_char in {'a', 'i', 'e'}:
            phonemes = ['w']
        else:
            phonemes = ['u']

    #
    # 't' is involved in two different affricates: /tl/ (eg as in the
    # absolutive suffix) and /ts/ when followed by 's'. If neither of these two
    # contexts is present, it simply maps to /t/.
    #
    elif current_char == 't':
        if next_char == 'l':
            phonemes = ['tK']
            new_char_idx += 1
        elif next_char in alveolar_sibilants:
            phonemes = ['ts']
            new_char_idx += 1
        else:
            phonemes = ['t']

    #
    # All of 's', 'ç', and 'z' map to /s/ in varying orthographies.
    #
    elif current_char in alveolar_sibilants:
        phonemes = ['s']

    #
    # We already accounted for some 'h' usages above. For the remaining cases,
    # if 'h' or 'j' are used, they typically correspond to the saltillo or
    # glottal fricative (aspiration in some modern variants). I represent all
    # of these cases as the glottal /?/.
    #
    elif current_char in {'h', 'j'}:
        phonemes = [saltillo]

    #
    # Usually, 'y' maps to the glide /j/ when followed by a vowel. In some
    # older orthographies, it also corresponds to /i/.
    #
    elif current_char == 'y':
        if next_char in all_vowels:
            phonemes = ['j']
        else:
            phonemes = ['i']

    #
    # All occurrences that I found of 'x' map to /S/.
    #
    elif current_char == 'x':
        phonemes = ['S']

    #
    # If the glottal stop (fricative in many modern varieties) also known as
    # the 'saltillo', is encoded by a diacritic on the vowel, we should return
    # two phonemes, Vowel and /?/.
    #
    elif current_char in saltillo2bare_vowels:
        phonemes = [saltillo2bare_vowels[current_char], saltillo]
        new_char_idx += 1

    elif current_char in ident_consonants:
        phonemes = [current_char]

    #
    # Not sure if this function should even be handling punctuation. For now,
    # just map the same punctuation character with a '<punc>' tag.
    #
    elif current_char in punctuation:
        phonemes = ["<punct>{}</punct>".format(current_char)]

    #
    # Letters corresponding to Spanish/non-Nahuatl phonemes
    #
    elif current_char in spanish_ident_consonants:
        phonemes = [current_char]
    elif current_char in spanish_ident_vowels:
        phonemes = [current_char]
    elif current_char in spanish_ident_consonants:
        phonemes = [current_char]

    else:
        raise ValueError("No phoneme mapping found for grapheme '{}'"
                         .format(current_char))

    return new_char_idx, phonemes


def nahuatl_word_g2p(word: str):
    """
    Produces a phonemic representation of the input word based on the rules
    of Nahuatl orthographies. The main g->p mapping function tries to account
    for many of the different orthographic varieties. A more exhaustive test
    data set, including more older written samples, should be collected at
    a future time.

    Parameters
    ----------
    word: str
        The word to be mapped to a phoneme sequence.

    Returns
    -------
    List of str
        A sequence of phonemes that should correspond to how the word is to be
        pronounced.

    """
    lowered_word = word.lower()
    num_chars = len(word)
    sampa = []
    uppercased_indices = []
    char_idx = 0
    while char_idx < num_chars:
        current_char = lowered_word[char_idx]
        next_char = (lowered_word[char_idx + 1]
                     if char_idx < (num_chars - 1)
                     else "")
        huiptla_char = (lowered_word[char_idx + 2]
                        if char_idx < (num_chars - 2)
                        else "")

        if word[char_idx].isupper():
            uppercased_indices.append(char_idx)

        char_idx, phonemes = map_grapheme_to_phoneme(char_idx,
                                                     current_char,
                                                     next_char,
                                                     huiptla_char)
        sampa.extend(phonemes)

    return sampa


def main(args_list=None):
    argparser = ArgumentParser()
    argparser.add_argument('input_file',
                           help="Path to file containing words you want to "
                                "convert to phonemic representation. Format "
                                "should be one word per line.")
    argparser.add_argument('--output_file', '-o',
                           help='Optional path to output file where phonemic '
                                'words will be stored, one word per line, '
                                'with phonemes separated by a single '
                                'whitespace. If this path is not provided, '
                                'phonemic words will be printed to standard '
                                'out in the same format.')
    if args_list is not None:
        args = argparser.parse_args(args_list)
    else:
        args = argparser.parse_args()

    phonemic_words = []
    with open(args.input_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            phoneme_list = nahuatl_word_g2p(line.strip())
            phonemic_words.append(" ".join(phoneme_list))

    if args.output_file is not None:
        with open(args.output_file, 'w') as fout:
            fout.write("\n".join(phonemic_words))
    else:
        print("\n".join(phonemic_words))


if __name__ == '__main__':
    main()
