from itertools import cycle

RESET = "\u001b[0m"
BLACK_TEXT = "\u001b[30m"
WHITE_BACKGROUND = "\u001b[47m"
BLACK_BACKGROUND = "\u001b[40m"
# Backgrounds:
backgrounds = [
    red,
    green,
    blue,
    magenta,
    cyan,
    yellow,
    bright_black,
    bright_cyan,
    bright_magenta,
    bright_blue,
    bright_yellow,
    bright_green,
    bright_red,
] = [
    "\033[37;41m",
    "\u001b[37;42m",
    "\u001b[37;44m",
    "\u001b[37;45m",
    "\u001b[37;46m",
    "\u001b[43m",
    "\u001b[37;100m",
    "\u001b[30;106m",
    "\u001b[30;105m",
    "\u001b[37;104m",
    "\u001b[30;103m",
    "\u001b[30;102m",
    "\u001b[30;101m",
]


class Groups:
    def __init__(self, syllable_lines):
        self.syllable_lines = syllable_lines
        self.id_to_group = dict()
        self.index_to_group = dict()
        self.pronunciations = None

    def add_syllable(self, group_id, index):
        assert group_id in self.id_to_group
        assert index not in self.index_to_group
        self.id_to_group[group_id].add(index)
        self.index_to_group[index] = group_id

    def remove_syllable(self, index):
        assert index in self.index_to_group
        group_id = self.index_to_group[index]
        del self.index_to_group[index]
        self.id_to_group[group_id].remove(index)
        if len(self.id_to_group[group_id]) == 0:
            del self.id_to_group[group_id]

    def add_group(self, group_id, group):
        self.id_to_group[group_id] = set(group)
        for index in group:
            self.index_to_group[index] = group_id

    def get_group(self, group_id):
        l = []
        for index in self.id_to_group[group_id]:
            syllable = self.get_syllable(index)
            l.append(syllable)
        return l

    def get_groups_in_range(self, curr_line_i, line_radius):
        groups_in_range = set()
        ranges = []
        ranges.append(range(curr_line_i, curr_line_i + line_radius + 1))
        ranges.append(range(curr_line_i - 1, curr_line_i - line_radius - 1, -1))

        actual_range = []
        for r in ranges:
            for l_i in r:
                if not 0 <= l_i < len(self.syllable_lines):
                    break
                # If end of verse
                if len(self.syllable_lines[l_i]) == 0:
                    break
                actual_range.append(l_i)

        for l_i in actual_range:
            if not 0 <= l_i < len(self.syllable_lines):
                break
            # If end of verse
            if len(self.syllable_lines[l_i]) == 0:
                break
            for w_i, word in enumerate(self.syllable_lines[l_i]):
                for p_i, pronun in enumerate(word):
                    for s_i in range(len(pronun)):
                        index = (l_i, w_i, p_i, s_i)
                        if index in self.index_to_group:
                            groups_in_range.add(self.index_to_group[index])
        return groups_in_range

    def get_syllable(self, index):
        value = self.syllable_lines
        for i in index:
            value = value[i]
        return value

    def set_pronunciations(self, final_pronunciations):
        assert len(final_pronunciations) == len(self.syllable_lines)
        self.pronunciations = final_pronunciations

    def to_text_lines(self, addresses=False):
        assert self.pronunciations is not None
        # Assign a color to each group
        group_id_to_color = {}
        colors = cycle(backgrounds)

        str_lines = []
        for line_number, line in enumerate(self.syllable_lines):
            line_string = ""
            for w_i, _ in enumerate(line):
                p_i = self.pronunciations[line_number][w_i]
                pronun = self.syllable_lines[line_number][w_i][p_i]
                for syl_i, syllable in enumerate(pronun):
                    syl_string = ""
                    # Add dashes between phonemes
                    syl_string = syl_string + "-".join(syllable)
                    if addresses:
                        syl_string += str((line_number, w_i, syl_i))
                    # If in group, give it a color
                    index = (line_number, w_i, p_i, syl_i)
                    if index in self.index_to_group:
                        group_id = self.index_to_group[index]
                        if group_id not in group_id_to_color:
                            if len(self.id_to_group[group_id]) < 2:
                                group_id_to_color[group_id] = WHITE_BACKGROUND
                            else:
                                group_id_to_color[group_id] = next(colors)
                        color = group_id_to_color[group_id]
                        syl_string = color + syl_string + WHITE_BACKGROUND + BLACK_TEXT
                    # If there are more syllables to the pronunciation,
                    #   add another dash afterwards
                    if syl_i + 1 < len(pronun):
                        syl_string += WHITE_BACKGROUND + "-"
                    line_string += syl_string

                # If word isn't the last word, add a space
                if w_i + 1 < len(line):
                    line_string += "  "
            str_lines.append(line_string)

        return str_lines

    def __str__(self):
        return BLACK_TEXT + WHITE_BACKGROUND + "\n".join(self.to_text_lines()) + RESET

    def str_with_text(self, text, addresses=False):
        ret_string = ""
        ret_string += BLACK_TEXT + WHITE_BACKGROUND
        syllable_color_lines = self.to_text_lines(addresses=addresses)
        for line_i, line in enumerate(text):
            ret_string += line
            ret_string += syllable_color_lines[line_i]
            if len(self.syllable_lines[line_i]) > 0:
                ret_string += "\n\n"
        ret_string += RESET
        return ret_string
