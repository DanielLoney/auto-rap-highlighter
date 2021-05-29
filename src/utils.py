import re, os, glob, errno, nltk
import numpy as np
import pandas as pd
from syllabifier import syllabifyARPA
import num2words

IGNORE_WORDS = set(['a', 'an', 'the', 'of', 'is,'])

try:
  CMUDICT = nltk.corpus.cmudict.dict()
except LookupError:
  nltk.download('cmudict')
  CMUDICT = nltk.corpus.cmudict.dict()

CMUDICT['em'] = [['EH', 'M'], ['AH', 'M']]
CMUDICT['lemme'] = [['L', 'EH', 'M', 'IY']]

def preprocess_text(src, ignored_reg_ex="[\[].*?[\]]|[^a-zA-Z0-9-' \n]"):
  file = open(src, 'rt')
  text = file.read()
  file.close()
  text = re.sub(ignored_reg_ex, "", text)
  text = re.sub("-", " ", text)
  text = re.sub(r"(\d+)", lambda x: num2words.num2words(int(x.group(0))), text)
  return text

def text_to_word_list(src, dest, filler):
  if not os.path.exists(src):
    print(src + " does not exist")
    return
  if not os.path.exists(dest):
    print(dest + " does not exist")
    return
  text = preprocess_text(src)
  words = [x.lower() for x in text.split()]
  base_name = os.path.splitext(os.path.basename(src))[0]
  with open(dest + "/" + base_name + "_word_list.txt", "w") as file:
    for i, word in enumerate(words[:-1]):
      if word not in CMUDICT:
        if re.sub("'", '', word) in CMUDICT:
            words[i] = re.sub("'", '', word)
        else:
            file.write(word + "\n")
            words[i] = filler
    file.write(words[-1])
  return words

def words_to_phonemes(src_dir, dest_dir, model_dir):
  if not os.path.exists(src_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src_dir)
  if not os.path.exists(dest_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),\
            dest_dir)
  if not os.path.exists(model_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), \
            model_dir)
  for input in glob.glob(src_dir + "/*.txt"):
    output = dest_dir + '/' + ''.join(os.path.basename(input) \
      .split("_")[:-2]) + "_pronunciations_list.txt"
    cmd = "g2p-seq2seq --decode " + input + \
      " --model_dir " + model_dir + " --output " + output
    os.system(cmd)

'''
returns list of pronunciations for each word in the word_list, subbing in
    unknown words

    syllable_n = [phoneme_1, phoneme_2, ..., phoneme_n]
    pronunciation_n = [syllable_1, syllable_2, ..., syllable_n]
    word_n = [pronunciation_1, ..., pronunciation_n]
    pronunciations_list = [word_1, word_2, ..., word_n]
'''
def word_list_to_pronunciations_list(unknown_src, word_list,\
        filler):
  if not os.path.exists(unknown_src):
    print(unknown_src + " does not exist")
    return

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
      syllabified.append(syllable.split(' '))
  except ValueError:
    syllabified.append(pronunciation)
  return syllabified

def get_unknown_word_phonemes(src):
  with open(src, "r") as phonemes:
    lines = phonemes.readlines()
    # list of phonemes
    unknown_word_phonemes = []
    for idx, line in enumerate(lines):
      # remove first word of each line and new line character
      word_phonemes = line.split(" ", 1)[1][:-1]
      unknown_word_phonemes.append(word_phonemes.split(" "))
  return unknown_word_phonemes

def remove_stress(pronunciation):
  ret = []
  for arpa in pronunciation:
    arpa = ''.join([l for l in arpa if not l.isdigit()])
    ret.append(arpa)
  return ret

def lookup_pronunciations(word):
  # Remove stress
  p_set = set()
  ps = []
  for p in CMUDICT[word]:
    no_stress = remove_stress(p)
    if tuple(no_stress) not in p_set:
      ps.append(no_stress)
    p_set.add(tuple(no_stress))

  return ps

'''
returns, 'syllable_lines' with syllables, pronunciations, words,
    lines in the format of the source text

    syllable = [phoneme1, phoneme2, ...]
    pronunciation = [syllable1, syllable2, ...]
    word = [pronunciation1, pronunciation2, ...]
    line = [word1, word2, word3, ...]
    syllable_lines = [line1, line2, ...]
'''
def pronunciations_list_to_syllable_lines(pronunciations_list, src,\
                          print_lines=False):
  def get_lines(src):
    text = preprocess_text(src)
    return text.splitlines()

  def skip_empty(idx):
    while idx < len(pronunciations_list) and pronunciations_list[idx] == '':
      idx += 1
    return idx

  syllable_lines = []
  # Set of words to ignore by (line index, word index)
  ignore_set = set()

  # Remove new_line character
  lines = [re.sub('\n', '', line) for line in get_lines(src)]
  # Turn into 2D array of words
  lines = [line.split() for line in lines]
  word_counter = 0

  for l_i, line in enumerate(lines):
    if print_lines:
      print(line)

    # If empty line, append empty list
    if line == ['']:
      syllable_lines.append([])
      continue

    num_words = len(line)

    # Make syllable_line
    syllable_line = []
    for w_i, w in enumerate(line):
      word = pronunciations_list[word_counter]
      syllable_line.append(word)
      word_counter += 1

      if w.lower() in IGNORE_WORDS:
          ignore_set.add((l_i, w_i))
    syllable_lines.append(syllable_line)

    if print_lines:
      print(syllable_line)

  return (syllable_lines, ignore_set)
'''
DEPRECATED

def __phones_to_list(src):
  if not os.path.exists(src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src)
  with open(src, "r") as phones:
    lines = phones.readlines()
    phones = []
    for idx, line in enumerate(lines):
      phones.append(line.split("\t", 1)[0])
  return phones

def phonemes_to_csv(phonemes_src, phones_src, dest_dir, word_radius,\
        separator=''):
  if not os.path.exists(phonemes_src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),\
            phonemes_src)
  if not os.path.exists(phones_src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),\
            phones_src)
  if not os.path.exists(dest_dir):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),\
            dest_dir)

  phoneme_radius = word_radius * 6
  phonemes = __phonemes_to_list(phonemes_src, separator)
  phones = __phones_to_list(phones_src)

  comatrix = pd.DataFrame(index=phones, columns=phones).fillna(0)
  comatrix['count'] = 0
  comatrix['word_radius'] = word_radius

  right_pointer = 0
  phones_so_far = 0
  ocurrences_in_range = {}

  for phoneme in phonemes:
    if phones_so_far < phoneme_radius and right_pointer < len(phonemes):
      if phoneme != separator:
        if phoneme not in ocurrences_in_range:
          ocurrences_in_range[phoneme] = 0
        ocurrences_in_range[phoneme] += 1
        phones_so_far += 1
      right_pointer += 1
    else:
      break

  def remove_ocurrence(idx):
    phoneme = phonemes[idx]
    if phoneme != separator:
      ocurrences_in_range[phoneme] -= 1
      if ocurrences_in_range[phoneme] == 0:
        del ocurrences_in_range[phoneme]
      #print("Subtracting: " + str(idx) + " " + phoneme)

  def add_ocurrence(idx):
    phoneme = phonemes[idx]
    if phoneme != separator:
      if phoneme not in ocurrences_in_range:
        ocurrences_in_range[phoneme] = 0
      ocurrences_in_range[phoneme] += 1
      #print("Adding: " + str(idx) + " " + phoneme)

  left_pointer = 0
  phones_seen = 0
  for idx, phoneme in enumerate(phonemes):
    if phoneme == separator:
      continue
    else:
      phones_seen += 1
      comatrix.at[phoneme, 'count'] += 1

    # add all co-ocurrent phonemes
    for key in ocurrences_in_range:
      ocurrences = ocurrences_in_range[key]
      # if key is the phoneme, subtract one for itself
      if key == phoneme:
        ocurrences -= 1
      # update co-ocurrence matrix with value
      comatrix.at[phoneme, key] += ocurrences

    if phones_seen >= phoneme_radius:
      remove_ocurrence(left_pointer)
      # Move left pointer to next non-separator phone
      left_pointer += 1
      while (phonemes[left_pointer] == separator):
        left_pointer += 1

    if right_pointer < len(phonemes) - 1:
      # Move right pointer to next non-separator phone
      right_pointer += 1
      while (phonemes[right_pointer] == separator):
        right_pointer += 1
      add_ocurrence(right_pointer)

  output_path = dest_dir + '/' + ''.join(os.path.basename(phonemes_src) \
    .split("_")[:-2])

  comatrix.to_csv(output_path + "_comatrix.csv")

  probmatrix = comatrix
  probmatrix[phones] = probmatrix[phones].div(comatrix['count'] *\
          phoneme_radius * 2, axis=1)
  probmatrix.to_csv(output_path + "_prob_comatrix.csv")

def multiple_phonemes_to_csv(phonemes_src_dir, phones_src,\
        dest_dir, word_radius, separator=''):
  for filepath in glob.glob(phonemes_src_dir + "/*.txt"):
    phonemes_to_csv(filepath, phones_src, dest_dir, word_radius, separator)
'''
