import unittest
from aline import aline, arpa2aline
import linkage

class GroupingTests(unittest.TestCase):
    san = ['S', 'AH', 'N']

    def test_arpa2aline(self):
        hustlin = arpa2aline.arpa2aline(['HH', 'AH', 'S', 'L', 'IH', 'N'])
        self.assertListEqual(hustlin, ['h', 'ʌ', 's', 'l', 'ɪ', 'n'])

        funkmaster = arpa2aline.arpa2aline(['F', 'AH', 'NG', 'K', 'M',\
                'AE', 'S', 'T', 'ER'])
        self.assertListEqual(funkmaster, ['f', 'ʌ', 'ŋ', 'k', 'm', 'æ', 's',\
            't', 'ɝ'])

    def test_align(self):
        self.assertListEqual(\
            linkage.align(self.san, self.san),\
            [[('s', 's'), ('ʌ', 'ʌ'), ('n', 'n')]])

        # Alignment for all arpa and itself gives a tuple of its converted
        # IPA
        d = arpa2aline.arpabet2aline_dict
        for arpa in d:
            alignment = [[(ipa, ipa) for ipa in d[arpa]]]
            with self.subTest(arpa=arpa):
                self.assertListEqual(\
                    linkage.align([arpa], [arpa]),\
                    alignment)

    def test_distance_identity(self):
        d1 = linkage.distance(self.san, self.san)
        self.assertEqual(d1, 0)

    def test_distance_diff_onsets(self):
        san2 = self.san
        with self.subTest():
            zan = ['Z', 'AH', 'N']
            d2 = linkage.distance(self.san, zan)
            self.assertEqual(d2, 0)
            d3 = linkage.distance(san2, zan)
            self.assertEqual(d3, 0)
        with self.subTest():
            span = ['S', 'P', 'AH', 'N']
            d2 = linkage.distance(self.san, span)
            self.assertEqual(d2, 0)
            d3 = linkage.distance(san2, span)
            self.assertEqual(d3, 0)


    # Identity lower than Near Rhymes lower than Non-Rhymes
    def test_distance_identity_near_rhyme_non_rhyme(self):

        d1 = linkage.distance(self.san, self.san)
        son = ['S', 'AO', 'N']
        d2 = linkage.distance(self.san, son)
        it = ['IH', 'T']
        d3 = linkage.distance(self.san, it)
        # d(san, san) < d(san, son) < d(san, it)
        self.assertTrue(d1 < d2 < d3)

    # Test extraneous phonemes
    def test_extraneous_coda(self):
        an = ['AH', 'N']
        ant = ['AH', 'N', 'T']
        # d(an, ant) > 0
        self.assertTrue(linkage.distance(an, ant) > 0)

    # Triangle Inequality

