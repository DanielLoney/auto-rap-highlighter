# Based on : https://github.com/jhasegaw/phonecodes/blob/master/src/phonecode_tables.py
arpabet2aline_dict = {
    'AA':'ɑ',
    'AE':'æ',
    'AH':'ʌ',
    'AH0':'ə',
    'AO':'ɔ',
    'AW':'aʊ',
    'AY':'aɪ',
    'EH':'ɛ',
    'ER':'ɝ',
    'EY':'eɪ',
    'IH':'ɪ',
    'IH0':'ɨ',
    'IY':'i',
    'OW':'oʊ',
    'OY':'ɔɪ',
    'UH':'ʊ',
    'UW':'u',
    'B':'b',
    'CH':'tʃ',
    'D':'d',
    'DH':'ð',
#    'EL':'l̩ ', # Unused by cmudict ((syllabic)
#    'EM':'m̩',# Unused by cmudict (syllabic)̩
#    'EN':'n̩', # Unused by cmudict (syllabic)
    'F':'f',
    'G':'g',
    'HH':'h',
    'JH':'dʒ',
    'K':'k',
    'L':'l',
    'M':'m',
    'N':'n',
    'NG':'ŋ',
    'P':'p',
    'Q':'ʔ',
    'R':'ɹ',
    'S':'s',
    'SH':'ʃ',
    'T':'t',
    'TH':'θ',
    'V':'v',
    'W':'w',
#    'WH':'ʍ', # Unused by cmudict
    'Y':'j',
    'Z':'z',
    'ZH':'ʒ'
}
'''Converts list of arpabet phonemes to aline IPA phonemes'''
def arpa2aline(arpa_phonemes):
    aline_phonemes = []
    for arpa in arpa_phonemes:
        if arpa not in arpabet2aline_dict:
            raise Exception(arpa + ' not found in list of known arpabet\
                phonemes')
        aline_phonemes.append(arpabet2aline_dict[arpa])
    return aline_phonemes
