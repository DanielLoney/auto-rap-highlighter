import unittest
from aline import aline, arpa2aline
import linkage, clustering
from tests.juicy_syllable_lines import juicy_syllable_lines

class linkage_tests(unittest.TestCase):
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
            [('s', 's'), ('ʌ', 'ʌ'), ('n', 'n')])

        # Alignment for all arpa and itself gives a tuple of its converted
        # IPA
        d = arpa2aline.arpabet2aline_dict
        for arpa in d:
            alignment = [(ipa, ipa) for ipa in d[arpa]]
            with self.subTest(arpa=arpa):
                self.assertListEqual(\
                    linkage.align([arpa], [arpa]),\
                    alignment)

    def test_distance_identity(self):
        d1 = linkage.distance(self.san, self.san)
        self.assertEqual(d1, 0)
        # print("d(san, san) = d(san,san) = {}".format(d1))

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
        # print("d(san, san) = {} < d(san, son) = {} < d(san, it) = {}".format(\
        #        d1, d2, d3))
    # Extraneous coda should affect distance
    def test_extraneous_coda(self):
        an = ['AH', 'N']
        ant = ['AH', 'N', 'T']
        d = linkage.distance(an, ant)
        # d(an, ant) > 0
        self.assertTrue(d > 0)
        # print("d(an, ant) = {} > 0".format(d))

        spain = ['S', 'P', 'EY', 'N']
        spay = ['S', 'P', 'EY']
        d = linkage.distance(spain, spay)
        # d(spain, spay) > 0
        self.assertTrue(d > 0)
        # print("d(spain, spay) = {} > 0".format(d))

    # Extraneous onset should not affect distance
    def test_extraneous_onset(self):
        pin = ['P', 'IH', 'N']
        spin = ['S', 'P', 'IH', 'N']
        # d(pin, spin) == 0
        self.assertTrue(linkage.distance(spin, pin) == 0)

    # TODO Alignment with two ipas in the same tuple
    # Triangle Inequality?

    def test_group_average_linkage(self):
        pin = ['P', 'IH', 'N']
        spin = ['S', 'P', 'IH', 'N']
        group1 = [tuple(pin)]
        group2 = [tuple(spin)]
        self.assertTrue(linkage.group_average_linkage(group1, group2) == 0)

        pint = ['P', 'IH', 'N', 'T']
        group2 = [tuple(pint)]
        self.assertTrue(linkage.group_average_linkage(group1, group2) > 0)

        group3 = [tuple(pin), tuple(pin), tuple(pint)]
        self.assertTrue(linkage.group_average_linkage(group1, group3) ==\
                linkage.distance(tuple(pin), tuple(pint)) / 3)



class clustering_tests(unittest.TestCase):
    def test_get_num_coda_consonants(self):
        spin = ['S', 'P', 'IH', 'N']
        self.assertTrue(clustering.get_num_coda_consonants(spin) == 1)

    def test_no_longer_live(self):
        live_groups = {0 : {'group': set(), 'most_recent_line': 0},\
                       1 : {'group': set(), 'most_recent_line': 1}}
        current_line = 3
        max_live_lines = 2

        _0_still_live = clustering.still_live(live_groups, current_line,\
            max_live_lines, 0)
        self.assertTrue(_0_still_live == False)

        _1_still_live = clustering.still_live(live_groups, current_line,\
            max_live_lines, 1)
        self.assertTrue(_1_still_live == True)

    def text_next_syllable_num_onsets(self):
        with self.assertRaises(AssertionError):
            clustering.next_syllable_num_onsets(0, [])
            clustering.next_syllable_num_onsets(0, [['AH'], ''])
            clustering.next_syllable_num_onsets(0, [['AH'], ['AH'], ['AH']])

        syllable_line = [['AH'], '', ['T', 'AH'], '', ['S', 'P', 'AH']]
        self.assertTrue(clustering.next_syllable_num_onsets(0, syllable_line\
                == 1))
        self.assertTrue(clustering.next_syllable_num_onsets(2, syllable_line\
                == 2))

    def test_has_next_syllable(self):
        syllable_line = [['AH'], '', ['AH']]
        self.assertTrue(clustering.has_next_syllable(0, syllable_line)\
                == True)
        self.assertTrue(clustering.has_next_syllable(2, syllable_line)\
                == False)

    def test_get_sorted_linkages(self):
        live_groups = {0: {'group': [tuple(['AH'])],\
            'most_recent_line': 0}}

        syllable = ['AH']
        expected = [(0, 0)]
        self.assertTrue(clustering.get_sorted_linkages(syllable, live_groups)\
                == expected)

        live_groups = {0: {'group': [tuple(['IH'])],\
            'most_recent_line': 0}, 1: {'group': [tuple(['AH'])],\
            'most_recent_line': 0}}
        expected = [(1, 0), (0, linkage.distance(syllable, ['IH']))]

        self.assertTrue(clustering.get_sorted_linkages(syllable, live_groups)\
                == expected)

    def test_best_num_consonants_to_give(self):
        live_groups = {0: {'group': [tuple(['AH'])],\
                'most_recent_line': 0},\
                1: {'group': [tuple(['IH'])], 'most_recent_line': 0}}
        syllable_line = [['AH', 'T', 'T', 'T', 'T'], '', ['AH']]
        current_index = 0
        (_, best_linkage_value) = \
            clustering.get_best_group_id_linkage_distance(\
                clustering.get_sorted_linkages(syllable_line[current_index],\
                    live_groups))

        d = linkage.group_average_linkage([tuple(['AH', 'T'])],\
                [tuple(['T', 'T', 'T', 'AH'])])
        best_num_cs = clustering.best_num_consonants_to_give(syllable_line,\
            live_groups, best_linkage_value, current_index)
        # print("Got (best average linkage, phoneme difference) =\
        #    {}".format(best_num_cs))
        self.assertTrue(best_num_cs == (0, d, -3))

        live_groups = {1: {'group': [tuple(['AH'])],\
                'most_recent_line': 0},\
                0: {'group': [tuple(['IH'])], 'most_recent_line': 0}}
        best_num_cs = clustering.best_num_consonants_to_give(syllable_line,\
            live_groups, best_linkage_value, current_index)
        # print("Got (best average linkage, phoneme difference) =\
        #    {}".format(best_num_cs))
        self.assertTrue(best_num_cs == (1, d, -3))

    def test_clustering(self):
        print("Groups are: \
            {}".format(clustering.cluster(juicy_syllable_lines)))
