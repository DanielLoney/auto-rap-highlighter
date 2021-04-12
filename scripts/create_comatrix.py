import argparse

parser = argparse.ArgumentParser()
# Args needed: separator, input directory, output directory, phones path
parser.add_argument("-p", "--phones", nargs=1, required=True,
        help='.phones file path with format the same as cmudict.phones')
parser.add_argument("-i", "--input", nargs='?', default='.',
        help='input directory path with .txt files of lyrics/literature')
parser.add_argument("-o", "--output", nargs='?', default='.',
        help='output directory path with for <name>_comatrix.csv files')
parser.add_argument("-s", "--separator", nargs='?', default='',
        help='output directory path with for <name>_comatrix.csv files')
args = parser.parse_args()


