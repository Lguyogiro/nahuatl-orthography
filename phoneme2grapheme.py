from argparse import ArgumentParser

sampa2long_vowels = {'e:': 'ē', 'o:': 'ō', 'a:': 'ā', 'i:': 'ī'}
aspirated_word_final_vowels2sampa = {
    'e': 'ê',
    'o': 'ô',
    'a': 'â',
    'i': 'î',
}

aspirated_word_medial_vowels2sampa = {
    'e': 'è',
    'o': 'ó',
    'a': 'à',
    'i': 'ì'
}


def classical(sampa_sequence):
    text = ""
    num_phonemes = len(sampa_sequence)
    char_idx = 0

    while char_idx < num_phonemes:
        phoneme = sampa_sequence[char_idx]
        next_phoneme = (sampa_sequence[char_idx + 1]
                        if char_idx < (num_phonemes - 1)
                        else "")
        if phoneme in 'aieopnlm ':
            text += phoneme
        elif phoneme == 'w':
            if next_phoneme.strip(':?') in {'a', 'i', 'e'}:
                text += 'hu'
            else:
                text += 'uh'
        elif phoneme == 'j':
            text += 'y'
        elif phoneme == 'tK':
            text += 'tl'

        elif phoneme == 'k':
            if next_phoneme.strip(':?') in {'i', 'e'}:
                text += 'qu'
            else:
                text += 'c'

        elif phoneme == 'tS':
            text += 'ch'

        elif phoneme == 'k_w':
            if not next_phoneme:
                text += 'uc'
            else:
                text += 'cu'

        elif phoneme == 'ts':
            text += 'tz'
        elif phoneme == 't':
            text += 't'
        elif phoneme == 'S':
            text += 'x'
        elif phoneme == 's':
            if next_phoneme.strip('?:') in 'ei':
                text += 'c'
            else:
                text += 'z'
        elif phoneme == '<es>s</es>':
            text += 's'

        elif phoneme == '?':
            text += 'h'

        elif phoneme in sampa2long_vowels:
            text += sampa2long_vowels[phoneme]
        elif phoneme in {"a", "e", "i", "o", "u"}:
            text += phoneme

        else:
            raise ValueError('Could not convert phoneme /{}/ to graphemes'
                             .format(phoneme))
        char_idx += 1

    return text


def sep(phonemic_word):
    text = ""
    num_phonemes = len(phonemic_word)
    char_idx = 0

    while char_idx < num_phonemes:
        phoneme = phonemic_word[char_idx]

        next_phoneme = (phonemic_word[char_idx + 1]
                        if char_idx < (num_phonemes - 1)
                        else "")

        if phoneme in 'aieopnskm ':
            text += phoneme

        elif phoneme == 'k_w':
            text += 'ku'

        elif phoneme == 'l':
            text += 'l'
            if next_phoneme == 'l':
                char_idx += 1

        elif phoneme == 'w':
            text += 'u'

        elif phoneme == 'j':
            text += 'y'

        elif phoneme == 'tK':
            text += 'tl'

        elif phoneme == 'tS':
            text += 'ch'

        elif phoneme == 'ts':
            text += 'ts'

        elif phoneme == 't':
            text += 't'

        elif phoneme == 'S':
            text += 'x'

        elif phoneme == '?':
            text += 'j'

        elif phoneme in sampa2long_vowels:
            text += sampa2long_vowels[phoneme]

        else:
            raise ValueError('Could not convert phoneme /{}/ to graphemes'
                             .format(phoneme))
        char_idx += 1

    return text


def launey(phonemic_word):
    text = ""
    num_phonemes = len(phonemic_word)
    char_idx = 0

    while char_idx < num_phonemes:
        phoneme = phonemic_word[char_idx]

        next_phoneme = (phonemic_word[char_idx + 1]
                        if char_idx < (num_phonemes - 1)
                        else "")

        huiptla_phoneme = (phonemic_word[char_idx + 2]
                           if char_idx < (num_phonemes - 2)
                           else "")

        if phoneme in 'pnl ':
            text += phoneme
        elif phoneme == 'w':
            if next_phoneme.strip(':') in {'a', 'i', 'e'}:
                text += 'hu'
            else:
                text += 'uh'
        elif phoneme == 'j':
            text += 'y'
        elif phoneme == 'tK':
            text += 'tl'

        elif phoneme == 'k':
            if next_phoneme.strip(':') in {'i', 'e'}:
                text += 'qu'
            else:
                text += 'c'
        elif phoneme == 'tS':
            text += 'ch'

        elif phoneme == 'k_w':
            if not next_phoneme:
                text += 'uc'
            else:
                text += 'cu'

        elif phoneme == 'ts':
            text += 'tz'

        elif phoneme == 'S':
            text += 'x'

        elif phoneme == 't':
            text += 't'

        elif phoneme == 's':
            if next_phoneme in {'e', 'i'}:
                text += 'c'
            else:
                text += 'z'

        elif phoneme == 'm':
            text += 'm'

        elif phoneme in 'aieo':
            if next_phoneme == '?':
                if not huiptla_phoneme:
                    text += aspirated_word_final_vowels2sampa[phoneme]
                else:
                    text += aspirated_word_medial_vowels2sampa[phoneme]
                char_idx += 1
            else:
                text += phoneme

        elif phoneme in sampa2long_vowels:
            text += sampa2long_vowels[phoneme]

        else:
            raise ValueError('Could not convert phoneme /{}/ to graphemes'
                             .format(phoneme))
        char_idx += 1

    return text


def main(args_list=None):
    argparser = ArgumentParser()
    argparser.add_argument('input_file',
                           help='Path to a file containing phonemic words, '
                                'one word per line')
    argparser.add_argument('orthography',
                           help='string indicating which orthography to use. '
                                'One of {classical, launey, or sep}')
    argparser.add_argument('--output_file', '-o',
                           help='Path to output file to store graphemic '
                                'words.')
    if args_list is not None:
        args = argparser.parse_args(args_list)
    else:
        args = argparser.parse_args()

    orth2func = {
        'classical': classical,
        'launey': launey,
        'sep': sep
    }
    orthographic_words = []
    with open(args.input_file) as f:
        for phonemic_word in f:
            phonemic_word = phonemic_word.strip().split()
            orthographic_word = orth2func[args.orthography](phonemic_word)
            orthographic_words.append(orthographic_word)
    if args.output_file is not None:
        with open(args.output_file, 'w') as fout:
            fout.write('\n'.join(orthographic_words))
    else:
        print('\n'.join(orthographic_words))


if __name__ == '__main__':
    main()
