import argparse, os, glob
import utils, clustering
from eval_group import evaluate_groups
from ansi2html import Ansi2HTMLConverter

parser = argparse.ArgumentParser()
# Args needed: separator, input directory, output directory, phones path
parser.add_argument("input_text",
        help='input directory path with .txt files of lyrics/literature')
parser.add_argument("phones_path",
        help='.phones file path with format the same as cmudict.phones')
parser.add_argument("model_dir_path",
        help='g2p model directory path')
parser.add_argument("-o", "--output_dir_path",
        help='output directory path with for <name>.html file')
phoneme_list_default = 'phoneme_lists'
parser.add_argument("-n", "--phoneme_list", \
        default=phoneme_list_default, \
        help='phoneme_list directory path where\
        <name>_phoneme_list.txt files go')
unknown_list_default = 'unknown_lists'
parser.add_argument("-w", "--unknown_list_dir", default=unknown_list_default,
        help='unknown_list_dir directory path where <name>_unknown_list.txt\
                files go')
parser.add_argument("-i", "--num_iterations", default=5, type=int,
        help='unknown_list_dir directory path where <name>_unknown_list.txt\
                files go')
parser.add_argument("-a", "--addresses_on", action='store_true',\
        default=False, \
        help='view the output with the addresses of each syllable')
parser.add_argument("-e", "--evaluate", action='store_true',\
        help='Return evaluation metrics for figaro, automatically replaces' +
        'input_text with "src/eval_group/figaro.txt" although positional'+
        'argument still required')
args = parser.parse_args()

assert args.num_iterations > 0

if args.evaluate:
    assert args.input_text == "src/eval_group/figaro.txt", "Evaluation only"+\
        "works with src/eval_group/figaro.txt as the input text"

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
pronunciations_list = utils.word_list_to_pronunciations_list(\
        unknown_phoneme_path, word_list, filler)
#print("Phoneme List is " + str(phoneme_list))
(syllable_lines, ignore_set) = utils.pronunciations_list_to_syllable_lines(\
        pronunciations_list, args.input_text)

print("Clustering...")
groups = clustering.cluster(syllable_lines, ignore_set, verse_tracking=False,\
        num_iterations=args.num_iterations)
with open(args.input_text) as f:
    text = f.readlines()
# Output
if args.output_dir_path is not None:
    html = Ansi2HTMLConverter().convert(groups.str_with_text(text))
    base_name = os.path.splitext(os.path.basename(args.input_text))[0]
    with open(args.output_dir_path + '/' + base_name + '.html', 'w') as f:
        f.write(html)
else:
    print(groups.str_with_text(text, addresses=args.addresses_on))

if args.evaluate:
    evaluate_groups.evaluate_groups(groups)
