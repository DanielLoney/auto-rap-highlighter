import re, os, glob, errno, nltk
from syllabifier import syllabifyARPA
import num2words

IGNORE_WORDS = set(["a", "an", "the", "of", "is,"])

try:
    CMUDICT = nltk.corpus.cmudict.dict()
except LookupError:
    nltk.download("cmudict")
    CMUDICT = nltk.corpus.cmudict.dict()

CMUDICT["em"] = [["EH", "M"], ["AH", "M"]]
CMUDICT["lemme"] = [["L", "EH", "M", "IY"]]


def preprocess_text(src, ignored_reg_ex="[\[].*?[\]]|[^a-zA-Z0-9-' \n]"):
    with open(src, "rt") as file:
        text = file.read()
        file.close()
        text = re.sub(ignored_reg_ex, "", text)
        text = re.sub("-", " ", text)
        text = re.sub(r"(\d+)", lambda x: num2words.num2words(int(x.group(0))), text)
        return text


def text_to_word_list(src, dest, filler):
    if not os.path.exists(src):
        print(src + " does not exist")
        return None
    if not os.path.exists(dest):
        print(dest + " does not exist")
        return None
    text = preprocess_text(src)
    words = [x.lower() for x in text.split()]
    base_name = os.path.splitext(os.path.basename(src))[0]
    with open(dest + "/" + base_name + "_word_list.txt", "w") as file:
        for i, word in enumerate(words[:-1]):
            if word not in CMUDICT:
                if re.sub("'", "", word) in CMUDICT:
                    words[i] = re.sub("'", "", word)
                else:
                    file.write(word + "\n")
                    words[i] = filler
        file.write(words[-1])
    return words


def words_to_phonemes(src_dir, dest_dir, model_dir):
    if not os.path.exists(src_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src_dir)
    if not os.path.exists(dest_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), dest_dir)
    if not os.path.exists(model_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), model_dir)
    for text in glob.glob(src_dir + "/*.txt"):
        output = (
            dest_dir
            + "/"
            + "".join(os.path.basename(text).split("_")[:-2])
            + "_pronunciations_list.txt"
        )
        cmd = (
            "g2p-seq2seq --decode "
            + text
            + " --model_dir "
            + model_dir
            + " --output "
            + output
        )
        os.system(cmd)


def word_list_to_pronunciations_list(unknown_src, word_list, filler):
    """
    returns list of pronunciations for each word in the word_list, subbing in
        unknown words

        syllable_n = [phoneme_1, phoneme_2, ..., phoneme_n]
        pronunciation_n = [syllable_1, syllable_2, ..., syllable_n]
        word_n = [pronunciation_1, ..., pronunciation_n]
        pronunciations_list = [word_1, word_2, ..., word_n]
    """
    if not os.path.exists(unknown_src):
        print(unknown_src + " does not exist")
        return None

    pronunciations_list = []
    unknown_word_phonemes = get_unknown_word_phonemes(unknown_src)
    counter = 0
    for word in word_list:
        assert len(word) > 0
        if word == filler:
            pronunciations = [unknown_word_phonemes[counter]]
            counter += 1
        else:
            pronunciations = lookup_pronunciations(word)
        syllabified_pronunciations = list(map(syllabify, pronunciations))
        pronunciations_list.append(syllabified_pronunciations)

    return pronunciations_list


def syllabify(pronunciation):
    syllabified = []
    try:
        for syllable in syllabifyARPA(pronunciation):
            syllabified.append(syllable.split(" "))
    except ValueError:
        syllabified.append(pronunciation)
    return syllabified


def get_unknown_word_phonemes(src):
    with open(src, "r") as phonemes:
        lines = phonemes.readlines()
        # list of phonemes
        unknown_word_phonemes = []
        for line in lines:
            # remove first word of each line and new line character
            word_phonemes = line.split(" ", 1)[1][:-1]
            unknown_word_phonemes.append(word_phonemes.split(" "))
    return unknown_word_phonemes


def remove_stress(pronunciation):
    ret = []
    for arpa in pronunciation:
        arpa = "".join([phoneme for phoneme in arpa if not phoneme.isdigit()])
        ret.append(arpa)
    return ret


def lookup_pronunciations(word):
    # Remove stress
    p_set = set()
    phonemes = []
    for phoneme in CMUDICT[word]:
        no_stress = remove_stress(phoneme)
        if tuple(no_stress) not in p_set:
            phonemes.append(no_stress)
        p_set.add(tuple(no_stress))

    return phonemes


def pronunciations_list_to_syllable_lines(pronunciations_list, src, print_lines=False):
    """
    returns, 'syllable_lines' with syllables, pronunciations, words,
        lines in the format of the source text

        syllable = [phoneme1, phoneme2, ...]
        pronunciation = [syllable1, syllable2, ...]
        word = [pronunciation1, pronunciation2, ...]
        line = [word1, word2, word3, ...]
        syllable_lines = [line1, line2, ...]
    """
    def get_lines(src):
        text = preprocess_text(src)
        return text.splitlines()

    syllable_lines = []
    # Set of words to ignore by (line index, word index)
    ignore_set = set()

    # Remove new_line character
    lines = [re.sub("\n", "", line) for line in get_lines(src)]
    # Turn into 2D array of words
    lines = [line.split() for line in lines]
    word_counter = 0

    for l_i, line in enumerate(lines):
        if print_lines:
            print(line)

        # If empty line, append empty list
        if line == [""]:
            syllable_lines.append([])
            continue

        # Make syllable_line
        syllable_line = []
        for w_i, word in enumerate(line):
            pronunciation = pronunciations_list[word_counter]
            syllable_line.append(pronunciation)
            word_counter += 1

            if word.lower() in IGNORE_WORDS:
                ignore_set.add((l_i, w_i))
        syllable_lines.append(syllable_line)

        if print_lines:
            print(syllable_line)

    return (syllable_lines, ignore_set)
