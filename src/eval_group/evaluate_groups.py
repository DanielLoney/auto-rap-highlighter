from eval_group.figaro_highlights import figaro_highlights
from groups import Groups
def highlights_to_dicts(highlights=figaro_highlights):
    address_to_group = {}
    group_id_to_set = {}
    for _id in figaro_highlights:
        members = set()
        for address in figaro_highlights[_id]:
            address_to_group[address] = _id
            members.add(address)
        group_id_to_set[_id] = members

    return (address_to_group, group_id_to_set)

def index_to_address(index):
    (l_i, w_i, p_i, s_i) = index
    return (l_i, w_i, s_i)

def get_cluster_stats(address_to_group, group_id_to_set, groups):
    def assess_index(index):
        address = index_to_address(index)
        tp = None
        tn = None
        fp = None
        fn = None
        group = groups.id_to_group[groups.index_to_group[index]]

        # unpaired in data but paired in groups
        if address not in address_to_group:
            tp = 0
            tn = num_syllables - len(group)
            fp = len(group) - 1
            fn = 0
        else:
            true_cluster = group_id_to_set[address_to_group[address]]
            tp = 0
            fp = 0
            for index in group:
                other = index_to_address(index)
                if other == address:
                    continue
                if other in true_cluster:
                    tp += 1
                else:
                    fp += 1
            group_negatives = num_syllables - len(group)
            data_negatives = num_syllables - len(true_cluster)
            tn = data_negatives - fp
            fn = group_negatives - tn

        assert tp != None
        assert tn != None and tn < num_syllables
        assert fp != None
        assert fn != None
        return (tp, tn, fp, fn)

    true_positive = 0 # pair is in the same subset in both clustering
    true_negative = 0 # pair in different cluster in both clusterings
    false_positive = 0 # pair same in groups but diff in data
    false_negative = 0 # pair diff cluster in groups but same in data

    # Find total number of syllables
    all_syllables = groups.index_to_group.keys()
    num_syllables = len(all_syllables)

    for index in all_syllables:
        (tp, tn, fp, fn) = assess_index(index)
        true_positive += tp
        true_negative += tn
        false_positive += fp
        false_negative += fn

    return (true_positive, true_negative, false_positive, false_negative)
def evaluate_groups(groups):
    (address_to_group, group_id_to_set) = highlights_to_dicts()
    (tp, tn, fp, fn) = get_cluster_stats(address_to_group, group_id_to_set,\
            groups)
    print("True Postives: {}, False Positives: {}".format(tp, fp))
    print("False Negatives: {}, True Negatives: {}".format(fn, tn))
    ri = (tp + tn) / (tp + tn + fp + fn)
    print("Rand Index: {}".format(ri))
