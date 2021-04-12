import re, os, glob, errno
import numpy as np
import pandas as pd

def texts_to_words(src, dest):
  if not os.path.exists(src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src)
  for filepath in glob.glob(src + "/*.txt"):
    file = open(filepath, 'rt')
    text = file.read()
    file.close()
    text = re.sub("[\[].*?[\]]|[^a-zA-Z-' \n]", "", text)
    words = [x.lower() for x in text.split()]
    base_name = os.path.splitext(os.path.basename("rap_lyrics/juicy.txt"))[0]
    # Overwrite by default
    with open(dest + "/" + base_name + "_word_list.txt", "w") as file:
      for word in words[:-1]:
        file.write(word + "\n")
      file.write(words[-1])

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
    .split("_")[:-2]) + "_comatrix.csv"
  comatrix.to_csv(output_path)

def multiple_phonemes_to_csv(phonemes_src_dir, phones_src,\
        dest_dir, word_radius, separator=''):
  for filepath in glob.glob(phonemes_src_dir + "/*.txt"):
    phonemes_to_csv(filepath, phones_src, dest_dir, word_radius, separator)

