from copy import deepcopy
from collections import namedtuple

import linkage
from groups import Groups

MAX_CODA_CONSONANTS = 5
MAX_ONSET_CONSONANTS = 3

_ClusterArgs = namedtuple(
    "ClusterArgs",
    "syllable_lines ignore_set linkage_criterion "
    + "verse_tracking max_live_lines num_iterations verbose",
)


class _ClusterIterVars:
    """Object to represent variables required for _cluster_iteration"""

    def __init__(self):
        self.next_group_id = None
        self.groups = None
        self.current_verse_starting_line = None
        self.live_groups = None
        self.final_pronunciations = None
        self.verse_dict = None
        self.current_verse_groups = None


def cluster(
    syllable_lines,
    ignore_set,
    linkage_criterion=10,
    verse_tracking=False,
    max_live_lines=1,
    num_iterations=5,
    verbose=True,
):
    """
    Clusters the syllable lines into groups.
    Turn on verse_tracking for easier debugging.

    Args:
        syllable_lines : 2D array, first dimension is lines, second
            dimension is syllable arrays (with arpabet phonemes) and separators

        ignore_set : Set of words to skip pronunciation checking for

        linkage_criterion : Max threshhold for group average linking
            between groups

        verse_tracking : Boolean to return a dictionary of verse IDs to
            a list of the group IDs for the groups that appear in the verse

        max_live_lines : Maximum distance between current line and other line
            for line to be considered "live"
    Returns:
        groups.Groups clustering of syllables, and verse_tracking info
    """

    # Create a cluser_args variable
    cluster_args = _ClusterArgs(
        syllable_lines,
        ignore_set,
        linkage_criterion,
        verse_tracking,
        max_live_lines,
        num_iterations,
        verbose,
    )
    _assert_valid_args(cluster_args)

    iter_vars = _init_iter_vars(cluster_args)

    if verbose:
        print("Iteration 1 of {}...".format(num_iterations))

    _cluster_groups(cluster_args, iter_vars)

    if verse_tracking:
        return (iter_vars.groups, iter_vars.verse_dict)
    return iter_vars.groups


def _assert_valid_args(cluster_args):
    assert cluster_args.num_iterations > 0
    assert cluster_args.max_live_lines >= 0
    assert cluster_args.linkage_criterion >= 0


def _init_iter_vars(cluster_args):
    # Set up variables for initial cluster iteration
    iter_vars = _ClusterIterVars()

    # cluster arguments
    # group id to group
    iter_vars.next_group_id = 0
    iter_vars.groups = Groups(
        cluster_args.syllable_lines
    )  # groups[group_id] = list(syllables)

    iter_vars.live_groups = dict()  # live_groups[_id] = {'group': set(syllables),
    #       'most_recent_line': int}

    # final_pronunciations: Gives pronunciation used for each word
    # line = [pronunciation_index_1, pronunciation_index_2, ...]
    # final_pronunciations = [line1, line2, ...]
    iter_vars.final_pronunciations = []

    if cluster_args.verse_tracking:
        _init_verse_tracking_iter_vars(iter_vars)

    return iter_vars


def _cluster_groups(cluster_args, iter_vars):

    # First iteration: Only checks preceding groups
    _cluster_iteration(cluster_args, iter_vars, first_iter=True)

    # Second iteration:
    #     For each syllable
    #         Remove it from its group
    #         Redetermine best_group_id using groups set from previous
    #         iteration
    for i in range(cluster_args.num_iterations - 1):
        if cluster_args.verbose:
            print("Iteration {} of {}...".format(i + 2, cluster_args.num_iterations))
        _cluster_iteration(cluster_args, iter_vars, first_iter=False)


def _cluster_iteration(cluster_args, iter_vars, first_iter=True):
    """Single cluster iteration, see cluster docstring for more info"""

    # Reset verse_tracking
    if cluster_args.verse_tracking:
        iter_vars.current_verse_starting_line = 0
        iter_vars.verse_dict = dict()  # current_verse_dict[line_#] = set(group_ids)
        iter_vars.current_verse_groups = set()

    for line_number, line in enumerate(cluster_args.syllable_lines):
        # List for each line
        if first_iter:
            iter_vars.final_pronunciations.append([])

        if len(line) == 0:
            _save_and_reset(cluster_args, iter_vars, first_iter, line_number)
            continue

        _update_live_groups(cluster_args, iter_vars, first_iter, line_number)

        for word_i, word in enumerate(line):
            # If the word is in the ignore set, just use the first
            # pronunciation
            if (line_number, word_i) in cluster_args.ignore_set:
                if first_iter:
                    iter_vars.final_pronunciations[line_number].append(0)
                continue
            if not first_iter:
                _reinsert_word(iter_vars, line_number, word_i, word)
            # Get best pronunciation
            p_i = get_best_pronunciation(word, iter_vars.groups, iter_vars.live_groups)

            # Update final_pronunciations
            if first_iter:
                iter_vars.final_pronunciations[line_number].append(p_i)
            else:
                iter_vars.final_pronunciations[line_number][word_i] = p_i

            pronun = word[p_i]
            for syllable_i, syllable in enumerate(pronun):
                # Check group linkage value of set([syllable]) and
                # live_groups

                indexes = (line_number, word_i, p_i, syllable_i)
                _check_syllable_and_update(
                    cluster_args, iter_vars, first_iter, indexes, syllable
                )

    iter_vars.groups.set_pronunciations(iter_vars.final_pronunciations)


def _check_syllable_and_update(cluster_args, iter_vars, first_iter, indexes, syllable):
    (line_number, word_i, p_i, syllable_i) = indexes
    sorted_base_syllable_linkages = _get_sorted_linkages(
        iter_vars.groups, syllable, iter_vars.live_groups
    )

    (
        best_group_id,
        best_linkage_value,
    ) = _get_best_group_id_linkage_distance(sorted_base_syllable_linkages)

    if best_linkage_value <= cluster_args.linkage_criterion:
        # Add the syllable to the best_group_id
        # Update groups
        iter_vars.groups.add_syllable(
            best_group_id, (line_number, word_i, p_i, syllable_i)
        )
        if first_iter:
            # Update live_groups
            iter_vars.live_groups[best_group_id] = {"most_recent_line": line_number}
    else:
        _add_new_group_and_update(
            cluster_args,
            iter_vars,
            first_iter,
            indexes,
        )


def _update_live_groups(cluster_args, iter_vars, first_iter, line_number):
    if first_iter:
        # Update live_groups
        new_live_groups = deepcopy(iter_vars.live_groups)
        for _id in iter_vars.live_groups:
            if not _still_live(
                iter_vars.live_groups, line_number, cluster_args.max_live_lines, _id
            ):
                del new_live_groups[_id]
        iter_vars.live_groups = new_live_groups
    elif not first_iter:
        # Update live_groups
        iter_vars.live_groups = iter_vars.groups.get_groups_in_range(
            line_number, cluster_args.max_live_lines
        )


def _reinsert_word(iter_vars, line_number, word_i, word):
    """Remove all syllables from groups and remove the group
    id associated with it if it was the only syllable left
    in the group"""
    for p_i, p in enumerate(word):
        for s_i in range(len(p)):
            index = (line_number, word_i, p_i, s_i)
            if index in iter_vars.groups.index_to_group:
                _id = iter_vars.groups.index_to_group[index]
                iter_vars.groups.remove_syllable(index)
                if _id not in iter_vars.groups.id_to_group:
                    iter_vars.live_groups.remove(_id)


def _save_and_reset(cluster_args, iter_vars, first_iter, line_number):
    if cluster_args.verse_tracking:
        # save
        if len(iter_vars.current_verse_groups) > 0:
            iter_vars.verse_dict[
                iter_vars.current_verse_starting_line
            ] = iter_vars.current_verse_groups

        # reset
        iter_vars.current_verse_starting_line = line_number + 1
        iter_vars.current_verse_groups = set()
    if first_iter:
        # reset live_groups
        iter_vars.live_groups = dict()


def _add_new_group_and_update(cluster_args, iter_vars, first_iter, indexes):
    """
    (line_number, word_i, p_i, syllable_i) = indexes
    """
    (line_number, word_i, p_i, syllable_i) = indexes
    # Update groups
    iter_vars.groups.add_group(
        iter_vars.next_group_id,
        [(line_number, word_i, p_i, syllable_i)],
    )
    # Update live_groups
    if first_iter:
        iter_vars.live_groups[iter_vars.next_group_id] = {
            "most_recent_line": line_number
        }
    else:
        iter_vars.live_groups.add(iter_vars.next_group_id)
    if cluster_args.verse_tracking:
        # Add to verse groups
        iter_vars.current_verse_groups.add(iter_vars.next_group_id)
    iter_vars.next_group_id += 1


def _init_verse_tracking_iter_vars(iter_vars):
    # Keep track of verse_first_line_#, current groupings_dict
    iter_vars.current_verse_starting_line = 0
    iter_vars.verse_dict = dict()  # current_verse_dict[line_#] = set(group_ids)
    iter_vars.current_verse_groups = set()


def get_best_pronunciation(word, groups, live_groups):
    """Given a list of pronunciations and the current live groups, give the
    best pronunciation"""
    best_p_i = 0
    best_linkage = float("inf")
    if len(word) == 1:
        return 0
    for (p_i, pronun) in enumerate(word):
        avg_linkage = 0
        for syllable in pronun:
            assert len(syllable) != 0
            sorted_base_syllable_linkages = _get_sorted_linkages(
                groups, syllable, live_groups
            )
            (_, linkage_value) = _get_best_group_id_linkage_distance(
                sorted_base_syllable_linkages
            )
            avg_linkage += linkage_value
        avg_linkage /= len(syllable)
        if avg_linkage < best_linkage:
            best_p_i = p_i
            best_linkage = avg_linkage
    return best_p_i


def _get_sorted_linkages(groups, syllable, live_groups):
    """
    Returns [(group_id, linkage_distance)] sorted by linkage_distance
    """
    live_group_linkages = [
        (_id, linkage.group_average_linkage(groups.get_group(_id), [tuple(syllable)]))
        for _id in live_groups
    ]

    return sorted(live_group_linkages, key=lambda pair: pair[1])


def _get_best_group_id_linkage_distance(sorted_linkages):
    if len(sorted_linkages) == 0:
        return (-1, float("inf"))
    return sorted_linkages[0]


def _still_live(live_groups, line_number, max_live_lines, _id):
    if _id not in live_groups:
        raise Exception("Id {} not in live groups".format(_id))
    return live_groups[_id]["most_recent_line"] >= line_number - max_live_lines


def _get_num_coda_consonants(syllable):
    num_coda_cs = 0
    for c in syllable[::-1]:
        if c not in linkage.arpa_vowels:
            num_coda_cs += 1
        else:
            break
    assert 0 <= num_coda_cs <= MAX_CODA_CONSONANTS
    return num_coda_cs
