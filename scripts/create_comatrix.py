import argparse, os
import comatrix_utils

parser = argparse.ArgumentParser()
# Args needed: separator, input directory, output directory, phones path
parser.add_argument("input_dir_path",
        help='input directory path with .txt files of lyrics/literature')
parser.add_argument("phones_path",
        help='.phones file path with format the same as cmudict.phones')
parser.add_argument("model_dir_path",
        help='g2p model directory path')
parser.add_argument("output_dir_path",
        help='output directory path with for <name>_comatrix.csv files')
phoneme_list_default = 'phoneme_lists'
parser.add_argument("-n", "--phoneme_list", \
        default=phoneme_list_default, \
        help='phoneme_list directory path where\
        <name>_phoneme_list.txt files go')
word_list_default = 'word_lists'
parser.add_argument("-w", "--word_list", default=word_list_default,
        help='word_lists directory path where <name>_word_list.txt files go')
parser.add_argument("-r", "--word_radius", default=10,
        help='radius around which phonemes are considered to be coocurring, \
                note: converted to phoneme radius by word radius * 6')
parser.add_argument("-s", "--separator", default='',
        help='separator string for word_list')
args = parser.parse_args()

if (args.phoneme_list == phoneme_list_default and\
        not os.path.exists('./' + phoneme_list_default)):
  os.mkdir('./' + phoneme_list_default)
if (args.word_list == word_list_default and\
        not os.path.exists('./' + word_list_default)):
  os.mkdir('./' + word_list_default)
comatrix_utils.texts_to_words(args.input_dir_path, args.word_list)
comatrix_utils.words_to_phonemes(args.word_list, args.phoneme_list,\
        args.model_dir_path)
comatrix_utils.multiple_phonemes_to_csv(args.phoneme_list, args.phones_path,\
        args.output_dir_path, word_radius=args.word_radius,\
        separator=args.separator)
