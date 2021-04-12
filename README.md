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
## Sources
- https://github.com/cmusphinx/g2p-seq2seq
  - README instructions inspired from this too 
- cmusphinx/g2p-seq2seq pretrained dictionary from sourceforge
- 
