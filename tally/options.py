import copy

from .decorators import verify_no_tables

class Options:
    """Options for both sheet and build with convenience methods to change both data and visuals. 
    """

    def __init__(self, table_options=None, formats=None, parent=None):
        if table_options is None:
            self.table_options = {
                "format":{
                    "base":{},
                    "percentage":{},
                    "counts":{}
                },
                "stub": {"ci":["c%"]},
                "banner_border": True,
                "annotations": False
            }
        else:
            self.table_options = table_options

        self.global_options = {
            "font_name": "Calibri",
            "font_size": "11"
        }

        self.formats = formats
        if formats is None:
            self.formats = {}
        self.parent = parent

    def set_base_position(self, position):
        """Change the position of the base

        Parameters
        ==========
        position: string
            Can be `outside`, `hidden` og `default`. Outside means it appears above the table's stub label.
        """
        if position == 'outside':
            self.set_question_format('base', {'font_color':'ffffff', 'bg_color':'ffffff', 'font_size':1})
        self.table_options['base'] = position

    def set_base_labels(self, label, unweighted_label="Unweighted base"):
        """Set the labels for the base and unweighted base.

        If this is not set, the bases will be called "weighted base" and "unweighted base". This can be used to change the base to "United Kingdom" or something that reflects the base.

        Parameters
        ==========
        label: string
            Main label for the base.
        unweighted_label: string
            Label for the unweighted base, if both are being shown.
        """

        self.table_options['base_label'] = label
        self.table_options['unweighted_base_label'] = unweighted_label

    def set_font(self, name, size=11):
        """Sets the global font name and size to be used in Excel.

        Parameters
        ==========
        name: string
            Font name
        size: int
            Font size
        """
        self.table_options['font_name'] = name
        self.global_options['font_name'] = name
        self.table_options['font_size'] = size
        self.global_options['font_size'] = size
        self.set_question_format('percentage', {'font_name':name, 'font_size':size})

    def set_language_key(self, text_key):
        """Set language key for results.

        Parameters
        ==========
        text_key: string
          Text key for the language, e.g. en-GB or jp-JP. The meta data has to have the available key present.
        """
        self.table_options['stub']['text_key'] = text_key

    def set_show_table_base_column(self, xtotal):
        """ Show column on the far left with the totals from all of the data.

        Parameters
        ==========
        xtotal: boolean
          Show/hide the total.
        """
        self.table_options['stub']['xtotal'] = xtotal

    def set_annotations(self, annotations):
        """Set whether tables are annotated with information about sig-testing, weight applied, and base.
       
        Parameters
        ==========
        annotations: boolean
          True if we want to see annotations under every table.
        """
        self.table_options['annotations'] = annotations

    def set_sig_test_levels(self,sig_test_level):
        """ Set alpha level for sig-testing.

        Parameters
        ==========
        sig_test_leve: int or array
            Integer or array of integers indicating the confidence level we want. No sig-tests are run if this isn't set.
        """
        if type(sig_test_level) == list:
            self.table_options['stub']['sig_level'] = sig_test_level
        else:
            self.table_options['stub']['sig_level'] = [sig_test_level]

    def set_hide_gridlines(self, hide):
        """Show or hide gridlines in the spreadsheet.

        Parameters
        ==========
        hide: integer
            0 Don't hide gridlines, 1 Hide printed gridlines only, 2 Hide screen and printed gridlines.
        """
        self._set_page_setup('hide_gridlines', {"option":hide})

    @verify_no_tables
    def set_stats(self, stats=['mean']):
        """Decide on what statistics to show
        """
        self.table_options['stub']['stats'] = stats

    @verify_no_tables
    def set_filter(self, filter):
        """Set filter to use on all data

        Parameters
        ==========
            filter: logical statement
                Logical statement, such as {'country':[1]} to use only country with code 1.
        """
        self.table_options['stub']['f'] = filter

    @verify_no_tables
    def set_ci(self, ci):
        """Set what the table cells should contain

        Parameters
        ==========
        ci: one or both of `c%`, `counts` to show percentages and/or counts.
        """
        self.table_options['stub']['ci'] = ci

    @verify_no_tables
    def set_show_bases(self, bases):
        """Set what bases should be shown in the table.

        Parameters
        ==========
        bases: list
            A list of strings, options are 'auto', 'weighted', 'unweighted', 'both', where auto will show the weighted base if there is a base, otherwise the unweighted one.
        """
        if bases not in ['auto', 'weighted', 'unweighted', 'both']:
            raise ValueError('Bases to show must be both, auto, weighted or unweighted')
        self.table_options['stub']['base'] = bases

    @verify_no_tables
    def set_stub(self, default_stub):
        """Set what variables should be in the stub.

        These can include any options used by DataSet.crosstab.
        """
        self.table_options['stub'] = {**self.table_options['stub'], **default_stub}

    @verify_no_tables
    def set_weight(self, weight):
        """Set the variable used to weight. 
        
        Every table will use this variable to weight its results if set.
        """
        self.table_options['stub']['w'] = weight

    @verify_no_tables
    def set_banner_border(self, border):
        """Set whether there should be a border between the banner categories, like gender and age.
        """
        self.table_options['banner_border'] = border

    def set_top_offset(self, offset_row):
        """Set where the data starts in the Excel sheet.
        """
        self.formats['offsets']['top'] = offset_row

    def freeze_panes(self, row=10, column=1):
        """Set where to freeze panes in the Excel file.
        """
        freeze = {
            "row": row,
            "col": column
        }
        self.formats['freeze_panes'] = freeze


    def set_row_colors(self, colors):
        """Set alternating row colors of the Excel spreadsheet
        Parameters
        ======
        colors: list
            list of colours that will be alternated across (supply two colours to get stripes)
        """
        if type(colors) == list:
            self.formats['row_colors'] = colors
        else:
            raise ValueError("The colours must be a list of one or more colours")

    def set_format(self, name, new_format):
        """Set format for a question type in the table

        Parameters
        ==========
        name: string (counts, percentage, stats, base)
        new_format: format dictionary, e.g. {'bold':True}
        """
        if name in self.formats:
            self.formats[name] = {**self.formats[name], **new_format}
        else:
            self.formats[name] = new_format

    @verify_no_tables
    def set_answer_format(self, answer_type, format):
        """ Set the format for an answer, e.g. Strongly agree, agree etc.

        """
        new_format = {0: {"format": format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}

    def set_question_format(self, answer_type, format):
        """Set the format rules for the question (line at the top of every table showing variable label)
        
        Parameters
        ==========
        answer_type : string (percentage, counts, stats, base)
        format : format dict, e.g. {'bold':True}
        """
        new_format = {"question": {"format": format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}

    @verify_no_tables
    def set_column_format_for_type(self, answer_type, column_index, format):
        """Set column format for answer type.

        Parameters
        ==========
         answer_type : string, percentage, counts, stats
         column_index : int
         format : format dict

        Example
        =======
        set_column_format_for_type('counts', 1, {'bold':True})
        """
        new_format = {column_index: {"format":format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}

    def _set_page_setup(self, key, value):
        if 'set_page_setup' not in self.formats:
            self.formats['set_page_setup'] = {}
        self.formats['set_page_setup'][key] = value

    def merge(self,  options):
        """ Merge two Option objects together, this one overriding the incoming one
        """
        self.table_options = self.merge_dict(self.table_options, copy.deepcopy(options.table_options))
        self.formats = self.merge_dict(self.formats, copy.deepcopy(options.formats))

    def merge_dict(self, source, destination):
        """ Merge two dictionaries by having the destination override the source, recursively.
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self.merge_dict(value, node)
            else:
                destination[key] = value

        return destination