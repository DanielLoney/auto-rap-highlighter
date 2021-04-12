import re, os, glob

def to_word_list(src, dest):
  if not os.path.exists(src):
    print(src + " does not exist")
    return
  for filename in glob.glob(src + "/*.txt"):
    file = open(filename, 'rt')
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

def to_phonemes():
    pass

