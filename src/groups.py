from itertools import cycle

reset = "\u001b[0m"
black_text = "\u001b[30m"
white_background = "\u001b[47m"
black_background = "\u001b[40m"
# Backgrounds:
backgrounds = [red, green, blue, magenta, cyan, yellow, bright_black,\
        bright_cyan, bright_magenta, bright_blue, bright_yellow,\
        bright_green, bright_red] =\
    ['\033[37;41m', '\u001b[37;42m', '\u001b[37;44m',\
    '\u001b[37;45m', '\u001b[46m', '\u001b[43m', '\u001b[37;100m',\
    '\u001b[30;106m', '\u001b[30;105m', '\u001b[37;104m',
    '\u001b[30;103m', '\u001b[30;102m', '\u001b[30;101m']

class Groups:
    def __init__(self, syllable_lines):
        self.syllable_lines = syllable_lines
        self.id_to_group = dict()
        self.index_to_group = dict()

    def add_syllable(self, group_id, line_index, syllable_index):
        assert group_id in self.id_to_group
        assert len(self.syllable_lines[line_index][syllable_index]) != 0
        self.id_to_group[group_id].add((line_index, syllable_index))
        self.index_to_group[(line_index, syllable_index)] = group_id

    def add_group(self, group_id, group):
        self.id_to_group[group_id] = set(group)
        for (line_index, syllable_index) in group:
            self.index_to_group[(line_index, syllable_index)] = group_id

    def get_group(self, group_id):
        l = []
        for (line_index, syllable_index) in self.id_to_group[group_id]:
            syllable = self.syllable_lines[line_index][syllable_index]
            l.append(syllable)
        return l

    def index_to_group(self, line_index, syllable_index):
        group_id = self.index_to_group[(line_index, syllable_index)]
        assert group_id is not None
        return group_id

    def to_text_lines(self, separator=''):
        # Assign a color to each group
        group_id_to_color = {}
        colors = cycle(backgrounds)
        for _id in range(len(self.id_to_group)):
            if len(self.id_to_group[_id]) < 2:
                group_id_to_color[_id] = white_background
            else:
                group_id_to_color[_id] = next(colors)

        str_lines = []
        for line_number, line in enumerate(self.syllable_lines):
            line_string = ''
            for syl_i, syllable in enumerate(line):
                # If empty space, append space to line
                if syllable == separator:
                    syl_string = '  '
                    line_string += syl_string
                # If syllable
                else:
                    syl_string = ''
                    syl_string = syl_string + '-'.join(syllable)
                    #print("Checking syllable: {}".format(syllable))
                    #print("Adding syl string {}".format(syl_string))
                    # If in group, give it a color
                    if (line_number, syl_i) in self.index_to_group:
                        group_id = self.index_to_group[(line_number, syl_i)]
                        color = group_id_to_color[group_id]
                        syl_string = color + syl_string +\
                            white_background + black_text
                    # If syllable is a part of a multi-syllable word
                    if syl_i > 0 and line[syl_i - 1] != separator:
                        syl_string = white_background + '-' + syl_string
                    line_string += syl_string
            str_lines.append(line_string)

        return str_lines

    def __str__(self):
        return black_text + white_background +\
                '\n'.join(self.to_text_lines()) + reset

    def str_with_text(self, text):
        s = ''
        s += black_text + white_background
        syllable_color_lines = self.to_text_lines()
        for line_i, line in enumerate(text):
            s += line
            s += syllable_color_lines[line_i]
            if len(self.syllable_lines[line_i]) > 0:
                s += '\n\n'
        s += reset
        return s

