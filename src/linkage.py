from memoization import cached
from aline import aline, arpa2aline

# TODO Check semivowel W, Y?
arpa_vowels = set(
    [
        "AA",
        "AE",
        "AH",
        "AO",
        "AW",
        "AY",
        "EH",
        "ER",
        "EY",
        "IH",
        "IY",
        "OW",
        "OY",
        "UH",
        "UW",
    ]
)

UNMATCHED = "-"


def syllable_list_to_no_onset_ipa(syllable):
    def remove_onset(syllable):
        first_vowel_index = 0
        while (
            first_vowel_index < len(syllable)
            and syllable[first_vowel_index] in aline.consonants
        ):
            first_vowel_index += 1
        if first_vowel_index == len(syllable):
            return syllable
        else:
            return syllable[first_vowel_index:]

    ipa = "".join(arpa2aline.arpa2aline(syllable))
    return remove_onset(ipa)


def align(phonemes1, phonemes2, already_ipa=False):
    """Returns a list of tuples for the alignment of list of phonemes,
    phonemes1 and list of phonemes, phonemes2"""

    if not already_ipa:
        phonemes1 = "".join(arpa2aline.arpa2aline(phonemes1))
        phonemes2 = "".join(arpa2aline.arpa2aline(phonemes2))

    return aline.align(phonemes1, phonemes2)[0]


@cached
def distance(
    syllable1,
    syllable2,
    extraneous_coda_penalty=4.9,
    vowel_delta_weight=2.6,
    consonant_delta_weight=0.7,
    unmatched_phoneme_penalty=4.9,
    debug_printing=False,
):
    """Returns an decimal distance between list of phonemes, syllable1 and
    list of phonemes, syllable2"""

    if debug_printing:
        print("Syllables are: {} and {}".format(syllable1, syllable2))
    ipas1 = syllable_list_to_no_onset_ipa(syllable1)
    ipas2 = syllable_list_to_no_onset_ipa(syllable2)

    alignment = align(ipas1, ipas2, already_ipa=True)
    if debug_printing:
        print("Alignments are: {}".format(alignment))
    dist = 0
    # Sum the deltas for each aligned phoneme
    for (a_1, a_2) in alignment:
        alignment_distance_component = 0
        for p_1 in a_1:
            for p_2 in a_2:
                if UNMATCHED in (p_1, p_2):
                    alignment_distance_component += unmatched_phoneme_penalty
                else:
                    weight = (
                        consonant_delta_weight
                        if (p_1 in aline.consonants or p_2 in aline.consonants)
                        else vowel_delta_weight
                    )
                    distance_component = weight * aline.delta(p_1, p_2)
                    alignment_distance_component += distance_component
        alignment_distance_component /= len(a_1) * len(a_2)
        dist += alignment_distance_component

    # Penalize unaligned phonemes
    num_phonemes = len(ipas1) if len(ipas1) > len(ipas2) else len(ipas2)
    if len(alignment) < num_phonemes:
        penalty = (num_phonemes - len(alignment)) * extraneous_coda_penalty
        dist += penalty
        if debug_printing:
            print(
                "Alignment off by "
                + str(num_phonemes - len(alignment))
                + " for rimes "
                + ipas1
                + " and "
                + ipas2
                + " penalty is "
                + str(penalty)
            )

    if debug_printing:
        print("Total distance is {}".format(dist))
    return dist


def group_average_linkage(group1, group2, distance=distance):
    _sum = 0
    assert isinstance(group1, list) and isinstance(group2, list)
    for syllable_1 in group1:
        for syllable_2 in group2:
            _sum += distance(tuple(syllable_1), tuple(syllable_2))
    return _sum / (len(group1) * len(group2))
