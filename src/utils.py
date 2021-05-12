import re, os, glob, errno, nltk
import numpy as np
import pandas as pd
from syllabifier import syllabifyARPA

def text_to_words(src, dest, filler):
  if not os.path.exists(src):
    print(src + " does not exist")
    return
  if not os.path.exists(dest):
    print(dest + " does not exist")
    return
  file = open(src, 'rt')
  text = file.read()
  file.close()
  text = re.sub("[\[].*?[\]]|[^a-zA-Z-' \n]", "", text)
  words = [x.lower() for x in text.split()]
  base_name = os.path.splitext(os.path.basename("rap_lyrics/juicy.txt"))[0]
  try:
    cmudict = nltk.corpus.cmudict.dict()
  except LookupError:
    nltk.download('cmudict')
    cmudict = nltk.corpus.cmudict.dict()
  with open(dest + "/" + base_name + "_word_list.txt", "w") as file:
    for i, word in enumerate(words[:-1]):
      if word not in cmudict:
        file.write(word + "\n")
        words[i] = filler
    file.write(words[-1])
  return word

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
      .split("_")[:-2]) + "_phoneme_list.txt"
    cmd = "g2p-seq2seq --decode " + input + \
      " --model_dir " + model_dir + " --output " + output
    os.system(cmd)

def __phonemes_to_list(src, separator=""):
  if not os.path.exists(src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src)
  phoneme_lists = []
  with open(src, "r") as phonemes:
    lines = phonemes.readlines()
    # list of phonemes with separator
    phonemes = []
    for idx, line in enumerate(lines):
      # remove first word of each line and new line character
      word_phonemes = line.split(" ", 1)[1][:-1]
      for phoneme in word_phonemes.split(" "):
        phonemes.append(phoneme)
      phonemes.append(separator)
    phonemes = phonemes[:-1]
  return phonemes

def __phones_to_list(src):
  if not os.path.exists(src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src)
  with open(src, "r") as phones:
    lines = phones.readlines()
    phones = []
    for idx, line in enumerate(lines):
      phones.append(line.split("\t", 1)[0])
  return phones

def phoneme_list_to_syllable_lines(phoneme_list, src, \
                          ignored_reg_ex="[\[].*?[\]]|[^a-zA-Z-' \n]",\
                          separator=''):
  def get_lines(src, ignored_reg_ex):
    text_file = open(src, 'rt')
    text = text_file.read()
    text = re.sub(ignored_reg_ex, "", text)
    text_file.close()
    return text.splitlines()

  def skip_empty(idx):
    while idx < len(phoneme_list) and phoneme_list[idx] == '':
      idx += 1
    return idx

  def syllabifyARPA_to_word_list(syllabifyARPAoutput):
    new_word = []
    for syllable in syllabifyARPAoutput:
      new_word.append(syllable.split(' '))
    return new_word

  lines = get_lines(src, ignored_reg_ex)
  curr_phoneme_idx = 0
  phoneme_lines = []
  for line in lines:
    print(line)
    processed_line = re.sub("\n", "", line)
    num_words = -1

    if processed_line == "":
      num_words = 0
    else:
      num_words = len(processed_line.split(' '))
    phoneme_line = []

    curr_phoneme_idx = skip_empty(curr_phoneme_idx)
    curr_phoneme = phoneme_list[curr_phoneme_idx]
    for _ in range(num_words):
      curr_phoneme = phoneme_list[curr_phoneme_idx]
      arpa_arr = []
      while curr_phoneme != '':
        arpa_arr.append(curr_phoneme)
        curr_phoneme_idx += 1
        if curr_phoneme_idx < len(phoneme_list):
          curr_phoneme = phoneme_list[curr_phoneme_idx]
        else:
          break
      phoneme_line += syllabifyARPA_to_word_list(syllabifyARPA(arpa_arr))
      phoneme_line.append(separator)
      curr_phoneme_idx += 1
    if len(phoneme_line) != 0:
      phoneme_line.pop()

    print(phoneme_line)
    phoneme_lines.append(phoneme_line)
  return phoneme_line
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

