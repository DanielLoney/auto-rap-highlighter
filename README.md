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
6. Install g2p-seq2seq
```
$ git clone https://github.com/cmusphinx/g2p-seq2seq.git
$ sudo python setup.py install (from the g2p-seq2seq directory)
```
## Running the Rhyming Dictionary
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

## Creating Phoneme Co-occurrence Matrices from text
Run the scripts/create_comatrix.py file.
For example:
```
python3 scripts/create_comatrix.py temp/text cmudict/cmudict.phones models/g2p-seq2seq-model-6.2-cmudict-nostress temp/comatrices -n temp/phoneme_list -w temp/word_list
```
### Instructions for scripts/create_comatrix.py
usage: create_comatrix.py [-h] [-n PHONEME_LIST] [-w WORD_LIST]
                          [-r WORD_RADIUS] [-s SEPARATOR]
                          input_dir_path phones_path model_dir_path
                          output_dir_path

positional arguments:
  input_dir_path        input directory path with .txt files of
                        lyrics/literature
  phones_path           .phones file path with format the same as
                        cmudict.phones
  model_dir_path        g2p model directory path
  output_dir_path       output directory path with for <name>_comatrix.csv
                        files

optional arguments:
  -h, --help            show this help message and exit
  -n PHONEME_LIST, --phoneme_list PHONEME_LIST
                        phoneme_list directory path where
                        <name>_phoneme_list.txt files go
  -w WORD_LIST, --word_list WORD_LIST
                        word_lists directory path where <name>_word_list.txt
                        files go
  -r WORD_RADIUS, --word_radius WORD_RADIUS
                        radius around which phonemes are considered to be
                        coocurring, note: converted to phoneme radius by word
                        radius * 6
  -s SEPARATOR, --separator SEPARATOR
                        separator string for word_list

## Sources
- https://github.com/cmusphinx/g2p-seq2seq
  - README instructions inspired from this too 
- cmusphinx/g2p-seq2seq pretrained dictionary from sourceforge
- 
