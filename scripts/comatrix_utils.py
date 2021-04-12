import re, os, glob, errno
import numpy as np
import pandas as pd

def to_word_list(src, dest):
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

def run_g2p(src_dir, dest_dir, model_dir):
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

def phonemes_to_list(src, separator=""):
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

def phones_to_list(src):
  if not os.path.exists(src):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src)
  with open(src, "r") as phones:
    lines = phones.readlines()
    phones = []
    for idx, line in enumerate(lines):
      phones.append(line.split("\t", 1)[0])
  return phone
