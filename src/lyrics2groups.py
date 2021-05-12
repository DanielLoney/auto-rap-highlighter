import argparse, os
import utils

parser = argparse.ArgumentParser()
# Args needed: separator, input directory, output directory, phones path
parser.add_argument("input_text",
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
unknown_list_default = 'unknown_lists'
parser.add_argument("-w", "--unknown_list", default=unknown_list_default,
        help='unknown_lists directory path where <name>_unknown_list.txt files go')
args = parser.parse_args()

if (args.phoneme_list == phoneme_list_default and\
        not os.path.exists('./' + phoneme_list_default)):
  os.mkdir('./' + phoneme_list_default)

if (args.unknown_list == unknown_list_default and\
        not os.path.exists('./' + unknown_list_default)):
  os.mkdir('./' + unknown_list_default)

filler = '**'
words = utils.text_to_words(args.input_text, args.unknown_list, filler)
utils.words_to_phonemes(args.unknown_list, args.phoneme_list,\
        args.model_dir_path)
