class Options:

    def __init__(self, table_options=None, formats={}):
        if table_options is None:
            self.table_options = {
                "format":{
                    "base":{},
                    "percentage":{},
                    "counts":{}
                },
                "stub": {"ci":["c%"]},
                "banner_border": True
            }
        else:
            self.table_options = table_options

        self.formats = formats

    def set_base_position(self, position):
        if position == 'outside':
            self.set_question_format('base', {'font_color':'ffffff', 'bg_color':'ffffff', 'font_size':1})
        self.table_options['base'] = position

    def set_show_table_base_column(self, xtotal):
        self.table_options['stub']['xtotal'] = xtotal

    def set_sig_test_levels(self,sig_test_level):
        if type(sig_test_level) == list:
            self.table_options['stub']['sig_level'] = sig_test_level
        else:
            self.table_options['stub']['sig_level'] = [sig_test_level]

    def set_hide_gridlines(self, hide):
        """
        0 Don’t hide gridlines.
        1 Hide printed gridlines only.
        2 Hide screen and printed gridlines.
        """
        self._set_page_setup('hide_gridlines', {"option":hide})

    def set_stats(self, stats=['mean']):
        self.table_options['stub']['stats'] = stats

    def set_ci(self, ci):
        self.table_options['stub']['ci'] = ci

    def set_show_bases(self, bases):
        if bases not in ['auto', 'weighted', 'unweighted', 'both']:
            raise ValueError('Bases to show must be both, auto, weighted or unweighted')
        self.table_options['stub']['base'] = bases

    def set_stub(self, default_stub):
        self.table_options['stub'] = {**self.table_options['stub'], **default_stub}

    def set_weight(self, weight):
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
        if name in self.formats:
            self.formats[name] = {**self.formats[name], **new_format}
        else:
            self.formats[name] = new_format

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

    def _set_page_setup(self, key, value):
        self.formats['set_page_setup'][key] = value

    def merge(self,  options):
        """ Merge two Option objects together, this one overriding the incoming one
        """
        self.table_options = self.merge_dict(self.table_options, options.table_options)
        self.formats = self.merge_dict(self.formats, options.formats)

    def merge_dict(self, source, destination):
        """
        >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
        >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
        >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self.merge_dict(value, node)
            else:
                destination[key] = value

        return destination