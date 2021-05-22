from copy import deepcopy
import linkage
from groups import Groups

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
MAX_CODA_CONSONANTS = 5
MAX_ONSET_CONSONANTS = 3

def cluster(syllable_lines, linkage_criterion=10, separator='',
        max_live_lines=1):

    # group id to group
    next_group_id = 0
    groups = Groups(syllable_lines) # groups[group_id] = list(syllables)

    # Keep track of verse_first_line_#, current groupings_dict
    current_verse_starting_line = 0
    verse_dict = dict() # current_verse_dict[line_#] = set(group_ids)
    current_verse_groups = set()

    live_groups = dict() # live_groups[_id] = {'group': set(syllables),
                         #       'most_recent_line': int}

    # First iteration: Look left
    for line_number, line in enumerate(syllable_lines):
        #print("Line: {}".format(line))

        # If empty line, save and reset variables
        if len(line) == 0:
            # save
            if len(current_verse_groups) > 0:
                verse_dict[current_verse_starting_line] =\
                        current_verse_groups

            # reset
            current_verse_starting_line = line_number + 1
            current_verse_groups = set()

            # reset live_groups
            live_groups = dict()
            continue
        else:
            # Update live_groups
            new_live_groups = deepcopy(live_groups)
            for _id in live_groups:
                if not still_live(live_groups, line_number, max_live_lines,\
                        _id):
                    del new_live_groups[_id]
            live_groups = new_live_groups

        for syllable_i, syllable in enumerate(line):
            #print("Syllable: {}".format(syllable))

            # Skip separators
            if syllable == separator:
                continue

            # Check group linkage value of set([syllable]) and
            # live_groups
            best_phoneme_difference = 0
            sorted_base_syllable_linkages = get_sorted_linkages(syllable,\
                live_groups)


            (best_group_id, best_linkage_value) = \
                get_best_group_id_linkage_distance(\
                    sorted_base_syllable_linkages)

            # print("Live groups: {}".format(live_groups))
            # print("Groups: {}".format(groups))

            if best_linkage_value <= linkage_criterion:
                # Add the syllable to the best_group_id
                # Update groups
                groups.add_syllable(best_group_id, line_number, syllable_i)
                updated_group = groups.get_group(best_group_id)
                #print("Syllable {} in group {}".format(syllable,\
                #    updated_group))
                # Update live_groups
                live_groups[best_group_id] = \
                    {'group': updated_group, 'most_recent_line': line_number}
            else:
                # Add the syllable as its own new group
                new_group = [syllable]
                # print("Adding new group: {}".format(new_group))
                # Update groups
                groups.add_group(next_group_id, [(line_number, syllable_i)])
                # Update live_groups
                live_groups[next_group_id] = \
                    {'group': new_group, 'most_recent_line': line_number}
                # Add to verse groups
                current_verse_groups.add(next_group_id)
                next_group_id += 1

    # Second iteration:
        # For each syllable
            # determine its average linkage to its group
            # Remove it from its group
            # Attempt to borrow phonemes and see if its linkage_distance
            #   improves
            # Add it to its new group with better linkage distance
            #   or back to its old group

            #(best_group_id, best_linkage_value, best_phoneme_difference) = \
            #    best_num_consonants_to_give(syllable_line, live_groups,\
            #        best_linkage_value, syllable_i)

    return (groups, verse_dict)

# Returns [(group_id, linkage_distance)] sorted by linkage_distance
def get_sorted_linkages(syllable, live_groups):
    live_group_linkages = [(_id, \
        linkage.group_average_linkage(live_groups[_id]['group'], \
            [tuple(syllable)])) for _id in live_groups]

    return sorted(live_group_linkages, key=lambda pair: pair[1])

def get_best_group_id_linkage_distance(sorted_linkages):
    if len(sorted_linkages) == 0:
        return (-1, float('inf'))
    else:
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
    assert num_coda_cs >= 0 and num_coda_cs <= MAX_CODA_CONSONANTS
    return num_coda_cs

def next_syllable_num_onsets(current_index, syllable_line,\
        separator=''):
    assert has_next_syllable(current_index, syllable_line)
    assert syllable_line[current_index + 1] == separator
    num_cs = 0
    while syllable_line[current_index + 2][num_cs] not in linkage.arpa_vowels:
        num_cs += 1

    assert num_cs >= 0 and num_cs <= MAX_ONSET_CONSONANTS
    return num_cs

def has_next_syllable(current_index, syllable_line):
    return current_index + 2 < len(syllable_line)

# Find the best number of consonants to give to get a better linkage
def best_num_consonants_to_give(syllable_line, live_groups,\
        best_linkage_value, current_index, separator=''):

    curr_syllable = syllable_line[current_index]
    num_coda_cs = get_num_coda_consonants(curr_syllable)
    best_phoneme_difference = 0
    best_group_id = -1

    if has_next_syllable(current_index, syllable_line):
        while num_coda_cs + best_phoneme_difference - 1 > 0 and\
            next_syllable_num_onsets(current_index, syllable_line) <\
                MAX_ONSET_CONSONANTS:

            new_syllable = curr_syllable[:(best_phoneme_difference - 1)]
            #print("Checking new_syllable: {}".format(new_syllable))
            # print("Codas left = {}".format(num_coda_cs +\
            #        best_phoneme_difference - 1))
            new_sorted_linkages = get_sorted_linkages(new_syllable, live_groups)

            (new_group_id, new_linkage_value) =\
                    get_best_group_id_linkage_distance(new_sorted_linkages)

            # update
            if new_linkage_value < best_linkage_value:
                best_linkage_value = new_linkage_value
                best_group_id = new_group_id
                best_phoneme_difference -= 1
            # End loop if no longer improving
            else:
                break

    return (best_group_id, best_linkage_value, best_phoneme_difference)
