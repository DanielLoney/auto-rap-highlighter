# Rap Rhyme Detection Project

## Setting up the virtual environment and dependencies

1. Install Python
2. Clone rhymerap repo
3. Install Pip
4. Install Pipenv
```
$ pip install --user pipenv
```
5. Install dependencies via Pipenv
In the rhymerap repo directory:
```
$ pipenv install
```
6. Install cmusphinx/g2p-seq2seq
```
$ git clone https://github.com/cmusphinx/g2p-seq2seq.git
$ python setup.py install (from the g2p-seq2seq directory)
```
7. Install vgautam/arpabet-syllabifier
```
$ git clone https://github.com/vgautam/arpabet-syllabifier
$ python setup.py install (from the arpabet-syllabifier directory)
```
## Running the Rhyming Dictionary
This section is based on the README from the cmusphinx/g2p-seq2seq repository
First run the pythonenv
```
$ pipenv shell

```
The cmusphinx/g2p-seq2seq pretrained model can be found in models/model_size-256_layers-3_filter-512_best.
To try out individual words, run the following:
```
$ g2p-seq2seq --interactive --model_dir model_folder_path
...
> hello
...
Pronunciations: [HH EH L OW]
...
>
```
For an English word list with one word per line run:
```
$ g2p-seq2seq --decode your_wordlist --model_dir model_folder_path [--output decode_output_file_path]
```
Word error rate can be found by running:
```
$ g2p-seq2seq --evaluate your_test_dictionary --model_dir model_folder_path
```
For the pretrained model:
```
Words: 13508
Errors: 4078
WER: 0.302
Accuracy: 0.698
```

## Creating Rhyming Groups
```
$ pipenv shell
$ python3 src/lyrics2groups.py temp/text/figaro.txt cmudict/cmudict.phones models/g2p-seq2seq-model-6.2-cmudict-nostress
```

## Instructions for scripts/create_comatrix.py
```
usage: lyrics2groups.py [-h] [-o OUTPUT_DIR_PATH] [-n PHONEME_LIST]
                        [-w UNKNOWN_LIST_DIR] [-i NUM_ITERATIONS]
                        input_text phones_path model_dir_path

positional arguments:
  input_text            input directory path with .txt files of
                        lyrics/literature
  phones_path           .phones file path with format the same as
                        cmudict.phones
  model_dir_path        g2p model directory path

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR_PATH, --output_dir_path OUTPUT_DIR_PATH
                        output directory path with for <name>.html file
  -n PHONEME_LIST, --phoneme_list PHONEME_LIST
                        phoneme_list directory path where
                        <name>_phoneme_list.txt files go
  -w UNKNOWN_LIST_DIR, --unknown_list_dir UNKNOWN_LIST_DIR
                        unknown_list_dir directory path where
                        <name>_unknown_list.txt files go
  -i NUM_ITERATIONS, --num_iterations NUM_ITERATIONS
                        unknown_list_dir directory path where
                        <name>_unknown_list.txt files go
```

## Running tests
From the source directory, run:
```
.../src$ python3 -m unittest tests.tests
```

## Sources
- https://github.com/cmusphinx/g2p-seq2seq
  - README instructions inspired from this too 
- cmusphinx/g2p-seq2seq pretrained dictionary from sourceforge
- https://github.com/nltk/nltk
- https://github.com/vgautam/arpabet-syllabifier
