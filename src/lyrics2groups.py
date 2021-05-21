import argparse, os, glob
import utils, clustering

parser = argparse.ArgumentParser()
# Args needed: separator, input directory, output directory, phones path
parser.add_argument("input_text",
        help='input directory path with .txt files of lyrics/literature')
parser.add_argument("phones_path",
        help='.phones file path with format the same as cmudict.phones')
parser.add_argument("model_dir_path",
        help='g2p model directory path')
#parser.add_argument("output_dir_path",
#        help='output directory path with for <name>_comatrix.csv files')
phoneme_list_default = 'phoneme_lists'
parser.add_argument("-n", "--phoneme_list", \
        default=phoneme_list_default, \
        help='phoneme_list directory path where\
        <name>_phoneme_list.txt files go')
unknown_list_default = 'unknown_lists'
parser.add_argument("-w", "--unknown_list_dir", default=unknown_list_default,
        help='unknown_list_dir directory path where <name>_unknown_list.txt\
                files go')
args = parser.parse_args()

if (args.phoneme_list == phoneme_list_default and\
        not os.path.exists('./' + phoneme_list_default)):
  os.mkdir('./' + phoneme_list_default)

if (args.unknown_list_dir == unknown_list_default and\
        not os.path.exists('./' + unknown_list_default)):
  os.mkdir('./' + unknown_list_default)

filler = '**'
separator = ''

# Remove previous unknown lists
for f in glob.glob(args.unknown_list_dir + '/*'):
    print("Unknown list deleted: {}".format(f))
    os.remove(f)

# Remove previous phoneme lists
for f in glob.glob(args.phoneme_list + '/*'):
    print("Phoneme list deleted: {}".format(f))
    os.remove(f)

word_list = utils.text_to_word_list(args.input_text,\
        args.unknown_list_dir, filler)
#print("Word list is " + str(word_list))
utils.words_to_phonemes(args.unknown_list_dir, args.phoneme_list,\
        args.model_dir_path)
def get_unknown_phoneme_path(directory):
    if (len(os.listdir(directory)) != 1):
      raise Exception("Expected only 1 unknown list in " + directory +\
              "Found {}".format(os.listdir(directory)))
    path = directory + '/' + os.listdir(directory)[0]
    return path
unknown_phoneme_path = get_unknown_phoneme_path(args.phoneme_list)
#print("Unknown path is " + str(unknown_phoneme_path))
phoneme_list = utils.phonemes_to_list(unknown_phoneme_path, word_list,\
        filler, separator)
#print("Phoneme List is " + str(phoneme_list))
syllable_lines = utils.phoneme_list_to_syllable_lines(phoneme_list,\
        args.input_text, separator=separator)

(groups, _) = clustering.cluster(syllable_lines)
with open(args.input_text) as f:
    text = f.readlines()
groups.print_with_text(text)
