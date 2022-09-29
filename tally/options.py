class Options:

    def __init__(self, table_options, formats):
        pass
        self.table_options = table_options
        self.formats = formats

    def set_base_position(self, position):
        if position == 'outside':
            self.set_question_format('base', {'font_color':'ffffff', 'bg_color':'ffffff', 'font_size':1})
        self.table_options['base'] = position

    def set_show_table_base_column(self, xtotal):
        self.table_options['stub']['xtotal'] = xtotal

    def set_sig_test_levels(self,sig_test_level):
        self.table_options['stub']['sig_level'] = [sig_test_level]

    def set_stats(self, stats=['mean']):
        self.table_options['stub']['stats'] = stats

    def set_default_ci(self, ci):
        self.table_options['stub']['ci'] = ci

    def set_default_show_bases(self, bases):
        if bases not in ['auto', 'weighted', 'unweighted', 'both']:
            raise ValueError('Bases to show must be both, auto, weighted or unweighted')
        self.table_options['stub']['base'] = bases

    def set_default_stub(self, default_stub):
        self.table_options['stub'] = {**self.table_options['stub'], **default_stub}

    def set_default_weight(self, weight):
        self.table_options['stub']['w'] = 'weight_a'

    def set_banner_border(self, border):
        self.table_options['banner_border'] = border

    def freeze_panes(self, row=10, column=1):
        freeze = {
            "row": row,
            "col": column
        }
        self.formats['freeze_panes'] = freeze


    def set_row_colors(self, colors):
        """
        Params:

        colors - list of colours that will be alternated across (supply to colours to get stripes)
        """
        if type(colors) == list:
            self.formats['row_colors'] = colors
        else:
            raise ValueError("The colours must be a list of one or more colours")

    def set_format(self, name, new_format):
        self.formats[name] = {**self.formats[name], **new_format}

    def set_answer_format(self, answer_type, format):
        new_format = {0: {"format": format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}

    def set_question_format(self, answer_type, format):
        new_format = {"question": {"format": format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}

    def set_column_format_for_type(self, answer_type, column_index, format):
        new_format = {column_index: {"format":format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}
