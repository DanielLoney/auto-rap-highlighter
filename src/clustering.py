from copy import deepcopy
import linkage
from groups import Groups

"""
args:
    syllable_lines : 2D array, first dimension is lines, second
    dimension is syllable arrays (with arpabet phonemes) and separators
returns:

    linkage_criterion : Max threshhold for group average linking
        between groups

    separator : blank space separator constant between words

    2D array of syllable lines, 2nd dimension is tuples of
    (syllable array, rhyming_group_id) or a separator
"""
MAX_CODA_CONSONANTS = 5
MAX_ONSET_CONSONANTS = 3



def cluster(
    syllable_lines,
    ignore_set,
    linkage_criterion=10,
    verse_tracking=False,
    max_live_lines=1,
    num_iterations=5,
):
    """
    Clusters the syllable lines into groups.
    Turn on verse_tracking for easier debugging.
    """

    assert num_iterations > 0
    num_iterations -= 1

    # group id to group
    next_group_id = 0
    groups = Groups(syllable_lines)  # groups[group_id] = list(syllables)

    if verse_tracking:
        # Keep track of verse_first_line_#, current groupings_dict
        current_verse_starting_line = 0
        verse_dict = dict()  # current_verse_dict[line_#] = set(group_ids)
        current_verse_groups = set()

    live_groups = dict()  # live_groups[_id] = {'group': set(syllables),
    #       'most_recent_line': int}

    # final_pronunciations: Gives pronunciation used for each word
    # line = [pronunciation_index_1, pronunciation_index_2, ...]
    # final_pronunciations = [line1, line2, ...]
    final_pronunciations = []

    # Given a list of pronunciations and the current live groups, give the
    # best pronunciation
    def get_best_pronunciation(word):
        best_p_i = 0
        best_linkage = float("inf")
        if len(word) == 1:
            return 0
        for (p_i, pronun) in enumerate(word):
            avg_linkage = 0
            for syllable in pronun:
                assert len(syllable) != 0
                sorted_base_syllable_linkages = get_sorted_linkages(
                    groups, syllable, live_groups
                )
                (_, linkage_value) = get_best_group_id_linkage_distance(
                    sorted_base_syllable_linkages
                )
                avg_linkage += linkage_value
            avg_linkage /= len(syllable)
            if avg_linkage < best_linkage:
                best_p_i = p_i
                best_linkage = avg_linkage
        return best_p_i

    # First iteration: Only checks preceding groups
    # Second iteration:
    #     For each syllable
    #         Remove it from its group
    #         Redetermine best_group_id using groups set from previous
    #         iteration

    def cluster_iteration(first_iter=True):
        nonlocal next_group_id
        nonlocal live_groups
        nonlocal groups
        nonlocal verse_dict
        nonlocal current_verse_starting_line
        nonlocal current_verse_groups
        # Reset verse_tracking
        if verse_tracking:
            current_verse_starting_line = 0
            verse_dict = dict()  # current_verse_dict[line_#] = set(group_ids)
            current_verse_groups = set()

        for line_number, line in enumerate(syllable_lines):
            if first_iter:
                final_pronunciations.append([])

            # If empty line, save and reset variables
            if len(line) == 0:
                if verse_tracking:
                    # save
                    if len(current_verse_groups) > 0:
                        verse_dict[current_verse_starting_line] = current_verse_groups

                    # reset
                    current_verse_starting_line = line_number + 1
                    current_verse_groups = set()
                if first_iter:
                    # reset live_groups
                    live_groups = dict()
                continue
            elif first_iter:
                # Update live_groups
                new_live_groups = deepcopy(live_groups)
                for _id in live_groups:
                    if not still_live(live_groups, line_number, max_live_lines, _id):
                        del new_live_groups[_id]
                live_groups = new_live_groups
            elif not first_iter:
                # Update live_groups
                live_groups = groups.get_groups_in_range(line_number, max_live_lines)

            for word_i, word in enumerate(line):
                if (line_number, word_i) in ignore_set:
                    if first_iter:
                        final_pronunciations[line_number].append(0)
                    continue
                if not first_iter:
                    # Remove all syllables from groups and remove the group
                    # id associated with it if it was the only syllable left
                    # in the group
                    for p_i, p in enumerate(word):
                        for s_i in range(len(p)):
                            index = (line_number, word_i, p_i, s_i)
                            if index in groups.index_to_group:
                                _id = groups.index_to_group[index]
                                groups.remove_syllable(index)
                                if _id not in groups.id_to_group:
                                    live_groups.remove(_id)
                # Get best pronunciation
                p_i = get_best_pronunciation(word)
                # Update final_pronunciations
                if first_iter:
                    final_pronunciations[line_number].append(p_i)
                else:
                    final_pronunciations[line_number][word_i] = p_i
                pronun = word[p_i]
                for syllable_i, syllable in enumerate(pronun):
                    # Check group linkage value of set([syllable]) and
                    # live_groups
                    sorted_base_syllable_linkages = get_sorted_linkages(
                        groups, syllable, live_groups
                    )

                    (
                        best_group_id,
                        best_linkage_value,
                    ) = get_best_group_id_linkage_distance(
                        sorted_base_syllable_linkages
                    )

                    if best_linkage_value <= linkage_criterion:
                        # Add the syllable to the best_group_id
                        # Update groups
                        groups.add_syllable(
                            best_group_id, (line_number, word_i, p_i, syllable_i)
                        )
                        if first_iter:
                            # Update live_groups
                            live_groups[best_group_id] = {
                                "most_recent_line": line_number
                            }
                    else:
                        # print("Adding new group: {}".format(new_group))
                        # Update groups
                        groups.add_group(
                            next_group_id, [(line_number, word_i, p_i, syllable_i)]
                        )
                        # Update live_groups
                        if first_iter:
                            live_groups[next_group_id] = {
                                "most_recent_line": line_number
                            }
                        else:
                            live_groups.add(next_group_id)
                        if verse_tracking:
                            # Add to verse groups
                            current_verse_groups.add(next_group_id)
                        next_group_id += 1
        groups.set_pronunciations(final_pronunciations)

    print("Iteration 1 of {}...".format(num_iterations + 1))
    cluster_iteration(first_iter=True)
    for i in range(num_iterations):
        print("Iteration {} of {}...".format(i + 2, num_iterations + 1))
        cluster_iteration(first_iter=False)

    if verse_tracking:
        return (groups, verse_dict)
    return groups


def get_sorted_linkages(groups, syllable, live_groups):
    '''
    Returns [(group_id, linkage_distance)] sorted by linkage_distance
    '''
    live_group_linkages = [
        (_id, linkage.group_average_linkage(groups.get_group(_id), [tuple(syllable)]))
        for _id in live_groups
    ]

    return sorted(live_group_linkages, key=lambda pair: pair[1])


def get_best_group_id_linkage_distance(sorted_linkages):
    if len(sorted_linkages) == 0:
        return (-1, float("inf"))
    return sorted_linkages[0]


def still_live(live_groups, line_number, max_live_lines, _id):
    if _id not in live_groups:
        raise Exception("Id {} not in live groups".format(_id))
    return live_groups[_id]["most_recent_line"] >= line_number - max_live_lines


def get_num_coda_consonants(syllable):
    num_coda_cs = 0
    for c in syllable[::-1]:
        if c not in linkage.arpa_vowels:
            num_coda_cs += 1
        else:
            break
    assert 0 <= num_coda_cs <= MAX_CODA_CONSONANTS
    return num_coda_cs
