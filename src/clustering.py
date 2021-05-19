import linkage

'''
args:
    syllable_lines : 2D array, first dimension is lines, second
    dimension is syllable arrays (with arpabet phonemes) and separators
returns:

    linkage_criterion : Max threshhold for group average linking
        between groups

    separator : blank space separator constant between words

    2D array of syllable lines, 2nd dimension is tuples of
    (syllable array, rhyming_group_id) or a separator
'''
def cluster(syllable_lines, linkage_criterion=20, separator='',
        max_live_lines=3):

    verse_num_to_line_groups = dict()
    # Retain dict[verse_first_line_#] = dict[line_#] = set(group_ids)

    # group id to group
    next_group_id = 0
    groups = dict() # groups[group_id] = set(syllables)

    # Keep track of verse_first_line_#, current groupings_dict
    current_verse = 0
    current_verse_dict = dict() # current_verse_dict[line_#] = set(group_ids)

    live_groups = dict() # live_groups[_id] = {'group': set(syllables),
                         #       'most_recent_line': int}

    # First iteration: Look left
    for line_number, line in enumerate(syllable_lines):

        # If empty line, save and reset variables
        if len(line) == 0:
            # save
            if len(current_verse_dict) > 0:
                verse_num_to_line_groups[current_verse] = current_verse_dict

            # reset
            current_verse = line_number + 1
            current_verse_dict = dict()

            # reset live_groups
            live_groups = dict()
            continue
        else:
            # Update live_groups
            for _id in live_groups:
                if not still_live(live_groups, line_number, max_live_lines,\
                        _id):
                    del live_groups[_id]

        for syllable_i, syllable in enumerate(syllable_lines):

            # Skip separators
            if syllable == separator:
                continue

            # Check group linkage value of set([syllable]) and
            # live_groups
            best_phoneme_difference = 0
            sorted_base_syllable_linkages = get_sorted_linkages(syllable,\
                live_groups)

            # Get # of coda consonants in syllable
            num_coda_cs = get_num_coda_consonants(syllable)

            (_, best_linkage_value) = \
                get_best_group_id_linkage_distance(\
                    sorted_base_syllable_linkages)

            # Check group linkage value of
            #   set([syllable] + next phoneme)
            #   and set([syllable] - final phoneme)
            # If grouping average increases, keep trying

            (best_linkage_value, best_phoneme_difference) = \
                best_num_consonants_to_give(syllable_line, live_groups,\
                    best_linkage_value, syllable_i)

            # Reset num_coda_cs
            num_coda_cs = get_num_coda_consonants(syllable)


            # Use the best version of the syllable and group it

            # If all groupings are still over the threshold put the
            # unaltered version of the syllable as its own group

            # Update line_groups
            # Update groups[id] = group
            # Update live_groups[id] = group
            # Update live_groups[id]['most_recent_line']
            pass

        current_verse_dict[line_number] = line_groups

    # Calculate sum of all syllable group averages

    # Future iterations: Look right, and left again
        # Again attempt the first iteration, this time if there is a
        # better grouping than the current one, change it.

            # Check groupings ahead
            # Check groupings behind
        # Repeat this iteration until total group average sum stagnates
        # TODO (For x steps?)

# Returns [(group_id, linkage_distance)] sorted by linkage_distance
def get_sorted_linkages(syllable, live_groups):
    live_group_linkages = [(_id, \
        linkage.group_average_linkage(live_groups[_id]['group'], \
            [tuple(syllable)])) \
        for _id in live_groups]

    return sorted(live_group_linkages, key=lambda pair: pair[1])

def get_best_group_id_linkage_distance(sorted_linkages):
    return sorted_linkages[0]

def still_live(live_groups, line_number, max_live_lines, _id):
    if _id not in live_groups:
        raise Exception('Id {} not in live groups'.format(_id))
    return live_groups[_id]['most_recent_line'] >= \
            line_number - max_live_lines

def get_num_coda_consonants(syllable):
    num_coda_cs = 0
    for c in syllable[::-1]:
        if c not in linkage.arpa_vowels:
            num_coda_cs += 1
        else:
            break
    return num_coda_cs

def next_syllable_num_onsets(current_index, syllable_line,\
        separator=''):
    assert has_next_syllable(current_index, syllable_line)
    assert syllable_line[current_index + 1] == separator
    num_cs = 0
    while syllable_line[current_index + 2][num_cs] not in linkage.arpa_vowels:
        num_cs += 1

    return num_cs

def has_next_syllable(current_index, syllable_line):
    return current_index + 2 < len(syllable_line)

# Find the best number of consonants to give to get a better linkage
def best_num_consonants_to_give(syllable_line, live_groups,\
        best_linkage_value, current_index, separator=''):

    curr_syllable = syllable_line[current_index]
    num_coda_cs = get_num_coda_consonants(curr_syllable)
    best_phoneme_difference = 0
    while has_next_syllable(current_index, syllable_line) and\
        num_coda_cs + best_phoneme_difference - 1 > 0 and\
        next_syllable_num_onsets(current_index, syllable_line) < 3:

        new_syllable = curr_syllable[:(best_phoneme_difference - 1)]
        #print("Checking new_syllable: {}".format(new_syllable))
        # print("Codas left = {}".format(num_coda_cs +\
        #        best_phoneme_difference - 1))
        new_sorted_linkages = get_sorted_linkages(new_syllable, live_groups)

        (_, new_linkage_value) =\
                get_best_group_id_linkage_distance(new_sorted_linkages)

        # update
        if new_linkage_value < best_linkage_value:
            best_linkage_value = new_linkage_value
            best_phoneme_difference -= 1
        # End loop if no longer improving
        else:
            break

    return (best_linkage_value, best_phoneme_difference)
