import argparse
import comatrix_utils

parser = argparse.ArgumentParser()
# Args needed: separator, input directory, output directory, phones path
parser.add_argument("-i", "--input", required=True,
        help='input directory path with .txt files of lyrics/literature')
parser.add_argument("-p", "--phones", required=True,
        help='.phones file path with format the same as cmudict.phones')
parser.add_argument("-m", "--model_dir", required=True,
        help='g2p model directory path')
parser.add_argument("-o", "--output", required=True,
        help='output directory path with for <name>_comatrix.csv files')
parser.add_argument("-n", "--phoneme_list", \
        default='phoneme_lists', \
        help='phoneme_list directory path where\
        <name>_phoneme_list.txt files go')
parser.add_argument("-w", "--word_list", default='word_lists',
        help='word_lists directory path where <name>_word_list.txt files go')
parser.add_argument("-r", "--word_radius", default=10,
        help='radius around which phonemes are considered to be coocurring, \
                note: converted to phoneme radius by word radius * 6')
parser.add_argument("-s", "--separator", default='',
        help='output directory path with for <name>_comatrix.csv files')
args = parser.parse_args()

comatrix_utils.texts_to_words(args.input, args.word_list)
comatrix_utils.words_to_phonemes(args.word_list, args.phoneme_list,\
        args.model_dir)
comatrix_utils.multiple_phonemes_to_csv(args.phoneme_list, args.phones,\
        args.output, word_radius=args.word_radius, separator=args.separator)
