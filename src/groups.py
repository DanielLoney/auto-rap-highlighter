from itertools import cycle

reset = "\u001b[0m"
black_text = "\u001b[30m"
white_background = "\u001b[47m"
black_background = "\u001b[40m"
# Backgrounds:
backgrounds = [red, green, blue, magenta, cyan, yellow, bright_black,
               bright_cyan, bright_magenta, bright_blue, bright_yellow,
               bright_green, bright_red] =\
    ['\033[37;41m', '\u001b[37;42m', '\u001b[37;44m',
     '\u001b[37;45m', '\u001b[37;46m', '\u001b[43m', '\u001b[37;100m',
     '\u001b[30;106m', '\u001b[30;105m', '\u001b[37;104m',
     '\u001b[30;103m', '\u001b[30;102m', '\u001b[30;101m']

class Groups:
    def __init__(self, syllable_lines):
        self.syllable_lines = syllable_lines
        self.id_to_group = dict()
        self.index_to_group = dict()

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
        ranges.append(
                range(curr_line_i - 1, curr_line_i - line_radius - 1, -1))

        actual_range = []
        for r in ranges:
            for l_i in r:
                if not (0 <= l_i and l_i < len(self.syllable_lines)):
                    break
                # Elif end of verse
                elif len(self.syllable_lines[l_i]) == 0:
                    break
                else:
                    actual_range.append(l_i)

        for l_i in actual_range:
            if not (0 <= l_i and l_i < len(self.syllable_lines)):
                break
            # Elif end of verse
            elif len(self.syllable_lines[l_i]) == 0:
                break
            for w_i, word in enumerate(self.syllable_lines[l_i]):
                for p_i, pronun in enumerate(word):
                    for s_i in range(len(pronun)):
                        index = (l_i, w_i, p_i, s_i)
                        if index in self.index_to_group:
                            groups_in_range.add(
                                    self.index_to_group[index])
        return groups_in_range

    def get_syllable(self, index):
        value = self.syllable_lines
        for i in index:
            value = value[i]
        return value

    def index_to_group(self, index):
        group_id = self.index_to_group[index]
        assert group_id is not None
        return group_id

    def set_pronunciations(self, final_pronunciations):
        assert len(final_pronunciations) == len(self.syllable_lines)
        self.pronunciations = final_pronunciations

    def to_text_lines(self, separator='', addresses=False):
        assert self.pronunciations != None
        # Assign a color to each group
        group_id_to_color = {}
        colors = cycle(backgrounds)

        str_lines = []
        for line_number, line in enumerate(self.syllable_lines):
            line_string = ''
            for w_i, word in enumerate(line):
                p_i = self.pronunciations[line_number][w_i]
                pronun = self.syllable_lines[line_number][w_i][p_i]
                for syl_i, syllable in enumerate(pronun):
                    syl_string = ''
                    # Add dashes between phonemes
                    syl_string = syl_string + '-'.join(syllable)
                    if addresses:
                        syl_string += str((line_number, w_i, syl_i))
                    # If in group, give it a color
                    index = (line_number, w_i, p_i, syl_i)
                    if index in self.index_to_group:
                        group_id = self.index_to_group[index]
                        if group_id not in group_id_to_color:
                            if len(self.id_to_group[group_id]) < 2:
                                group_id_to_color[group_id] =\
                                        white_background
                            else:
                                group_id_to_color[group_id] =\
                                        next(colors)
                        color = group_id_to_color[group_id]
                        syl_string = color + syl_string +\
                            white_background + black_text
                    # If there are more syllables to the pronunciation,
                    #   add another dash afterwards
                    if syl_i + 1 < len(pronun):
                        syl_string += white_background + '-'
                    line_string += syl_string

                # If word isn't the last word, add a space
                if w_i + 1 < len(line):
                    line_string += '  '
            str_lines.append(line_string)

        return str_lines

    def __str__(self):
        return black_text + white_background +\
                '\n'.join(self.to_text_lines()) + reset

    def str_with_text(self, text, addresses=False):
        s = ''
        s += black_text + white_background
        syllable_color_lines = self.to_text_lines(addresses=addresses)
        for line_i, line in enumerate(text):
            s += line
            s += syllable_color_lines[line_i]
            if len(self.syllable_lines[line_i]) > 0:
                s += '\n\n'
        s += reset
        return s

