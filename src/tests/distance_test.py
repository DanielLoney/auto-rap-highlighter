import unittest
from aline import aline, arpa2aline

class GroupingTests(unittest.TestCase):

    def test_arpa2aline(self):
        hustlin = arpa2aline.arpa2aline(['HH', 'AH', 'S', 'L', 'IH', 'N'])
        self.assertListEqual(hustlin, ['h', 'ʌ', 's', 'l', 'ɪ', 'n'])

        funkmaster = arpa2aline.arpa2aline(['F', 'AH', 'NG', 'K', 'M',\
                'AE', 'S', 'T', 'ER'])
        self.assertListEqual(funkmaster, ['f', 'ʌ', 'ŋ', 'k', 'm', 'æ', 's',\
            't', 'ɝ'])

    def test_align(self):
        self.assertListEqual(\
            linkage.align(['S', 'AH', 'N'], ['S', 'AH', 'N']),\
            [[('s', 's'), ('ʌ', 'ʌ'), ('n', 'n')]])

        self.assertListEqual(\
            linkage.align(['S', 'AH', 'N'], ['S', 'AH', 'N']),\
            [[('s', 's'), ('ʌ', 'ʌ'), ('n', 'n')]])

        # Alignment for all arpa and itself gives a tuple of its converted
        # IPA
        for arpa in arpabet2aline_dict:
            self.assertListEqual(\
                linkage.align([arpa], [arpa]),\
                [[(arpabet2aline_dict[arpa], arpabet2aline_dict[arpa])]])
