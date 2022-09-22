import pandas as pd
import json
from openpyxl import load_workbook
from openpyxl.styles import Font

from .build_defaults import build_default_formats


class Build:
    """
    A class that gathers together crosstabs a user wants to use to build Excel, Powerpoint or Datasmoothie dashboards output. 

    Parameters
    ----------
      name: string
        Name for the dataset
    """

    def __init__(self, name=None, subtitle=None, default_dataset=None, table_of_contents=False):
        self.name = name
        self.subtitle = subtitle
        self.default_dataset = default_dataset
        self.table_of_contents = table_of_contents
        self.sheets = []

    def add_sheet(self, name=None, banner='@'):
        sheet = Sheet(banner=banner, default_dataset=self.default_dataset)
        self.sheets.append(sheet)
        return sheet

    def save_excel(self, filename):
        dataframes_payload = []
        formats = []
        for sheet in self.sheets:
            df = sheet.combine_dataframes()
            df = df.replace({'null':0})
            payload = json.loads(df.to_json(orient='split'))
            payload['index_names'] = df.index.names.copy()
            payload['column_names'] = df.columns.names.copy()
            dataframes_payload.append(payload)        
            formats.append(sheet.formats)

        self.default_dataset.build_excel_from_dataframes(filename=filename, dataframes=dataframes_payload, client_formats=formats)


        # add table of contents
        if len(self.sheets)>1:
            offset_y = 10

            wb = load_workbook(filename)
            wb_sheet = wb.create_sheet('Contents', 0)
            wb_sheet.cell(row=offset_y, column=2, value='Contents')
            wb_sheet.column_dimensions['B'].width = 20
            wb_sheet.column_dimensions['C'].width = 70

            if self.name is not None:
                title = wb_sheet.cell(3, 2, value=self.name)
                title.font = Font(size="20")
            if self.subtitle is not None:
                subtitle = wb_sheet.cell(4, 2, value=self.subtitle)
                subtitle.font = Font(size="14")
            for index, sheet in enumerate(self.sheets):
                wb_sheet.cell(row=index+1+offset_y, column=3, value=sheet.get_name())
                link_value = '=HYPERLINK("#{}!A1", "Table {}")'.format(wb.sheetnames[index+1], index+1)
                cell = wb_sheet.cell(row=index+1+offset_y, column=2, value=link_value)
                cell.font = Font(color="2A64C5", underline="single")

        wb.save(filename)

class Sheet:
    def __init__(self, banner='@', default_dataset=None, name=None):
        self.banner = banner
        self.dataframes = []
        self.default_dataset = default_dataset
        self.options = {}
        self.name = name
        self.formats = build_default_formats
        self.table_options = {
            "base": {},
            "format":{
                "base":{},
                "percentage": {},
                "counts": {},
            },
            "stub": {"ci":["c%"]}
        }
        self.set_question_format('percentage', {'text_wrap':True})
        self.set_question_format('counts', {'text_wrap':True})

    def get_name(self):
        if self.name is not None:
            return self.name
        else:
            if len(self.dataframes)>0:
                name = self.dataframes[0].index.get_level_values(0)[0]
                if name == 'Base':                       
                    return self.dataframes[0].index.get_level_values(0)[1]
                else:
                    return name
            else:
                return ""

    def set_base_position(self, position):
        if position == 'outside':
            self.set_question_format('base', {'font_color':'#ffffff', 'bg_color':'#ffffff', 'font_size':1})
        self.table_options['base'] = position

    def set_show_table_base_column(self, xtotal):
        self.table_options['stub']['xtotal'] = xtotal

    def set_sig_test_levels(self,sig_test_level):
        self.table_options['stub']['sig_level'] = [sig_test_level]

    def set_default_ci(self, ci):
        self.table_options['stub']['ci'] = ci

    def set_default_stub(self, default_stub):
        self.table_options['stub'] = {**self.table_options['stub'], **default_stub}

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

    def set_column_format(self, answer_type, column_index, format):
        new_format = {column_index: {"format":format}}
        old_format = self.table_options['format'][answer_type]
        self.table_options['format'][answer_type] = {**old_format, **new_format}

    def add_table(self, stub, options={}, dataset=None):
        if self.default_dataset and dataset is None:
            dataset = self.default_dataset
        crosstab = {**{**self.table_options['stub'], **stub}, **{'y':self.banner, 'add_format_column':True}}
        df = dataset.crosstab(
            crosstabs=[crosstab]
        )
        options = {**self.table_options, **options}
        # the format column should always have a cell_options key
        df['FORMAT'] = df['FORMAT'].apply(lambda x: json.dumps({**json.loads(x), **{'cell_format':{}}}))
        df = self.apply_sheet_options(df, self.options)
        df = self.apply_table_options(df, options)
        self.dataframes.append(df)

    def apply_sheet_options(self, df, options):
        if 'pull_base_up' in options:
            if options['pull_base_up'] == False:
                # we need to hide the 'question'
                new_format = {
                        "original_type":"base",
                        "question":{ 
                            "format": {"font_color":"#FFFFFF", "bg_color":"#ffffff"}
                        }
                }
                df = self.set_format_for_type(df, 'base', new_format)
                df['FORMAT'] = df['FORMAT'].str.replace('"type\": \"base\"','\"type\": \"counts\"')
        return df

    def apply_table_options(self, df, options):
        if 'base' in options:
            df = self.apply_base_options(df, options['base'])
        if 'base_label' in options:
            df = df.rename(index={'Base':options['base_label']}, level=1)
        if 'format' in options:
            df = self.apply_table_format_options(df, options['format'])
        if 'row_format' in options:
            df = self.set_row_format(df, options['row_format'])
        return df

    def apply_table_format_options(self, df, options):
        if 'base' in options:
            new_format = options['base']
            df = self.set_format_for_type(df, 'base', new_format)
        if 'percentage' in options:
            new_format = options['percentage']
            df = self.set_format_for_type(df, 'percentage', new_format)
        return df

    def set_row_format(self, df, format):
        def apply_row_format(x, new_format):
            current_format = json.loads(x)
            for i in list(range(df.shape[1])):
                if str(i) in current_format['cell_format']:
                    current_format['cell_format'][str(i)]['format'] = {**current_format['cell_format'][str(i)]['format'], **new_format['format']}
                else:
                    current_format['cell_format'][str(i)] = {'format':new_format['format']}
            return json.dumps(current_format)
        for row in format['rows']:
            df.iat[row, -1] = apply_row_format(df.iloc[row, -1], format)
        return df        

    def set_format_for_type(self, df, type, format):
        """ Method to add/alter format json per cell or per question type.

        Parameters:
            type (string): can be base, count, percentage or any type returned by the Tally API
            format (dict): what gets merged with cell_format
        """
        def apply_format(x, new_format):
            old_format = json.loads(x)
            resulting_format = old_format
            resulting_format['cell_format'] = {**old_format['cell_format'], **new_format}
            return json.dumps(resulting_format)

        new_format = format

        # set index temporarily to (question, 0), (question, 1) ... to insure unique indices
        question = df.index.levels[0].values[0]
        old_index = df.index
        df.index = pd.MultiIndex.from_tuples([(question, i) for i in range(df.shape[0])])
        location = df[df['FORMAT'].str.contains(f'\"type\": \"{type}\"')].index
        if len(location) == 0:
            location = df[df['FORMAT'].str.contains(f'\"original_type\": \"{type}\"')].index
        df.at[location, ('FORMAT',)] = df.loc[location]['FORMAT'].apply(apply_format, args=[new_format])
        df.index = old_index
        df.index = df.index.set_names(['Question', 'Values'])
        return df

    def apply_base_options(self, df, option):
        if option == 'hide':
            if 'Unweighted base' in df.index.get_level_values(1):
                df = df.drop('Unweighted base', level=1)
            if 'Base' in df.index.get_level_values(1):            
                df = df.drop('Base', level=1)
        elif option == 'outside':
            bases = df.xs('Base', level=1)
            tuples = [("Base", "Base")]*bases.shape[0]
            bases.index = pd.MultiIndex.from_tuples(tuples)
            if 'Unweighted base' in df.index.get_level_values(1):
                unweighted_bases = df.xs('Unweighted base', level=1)
                tuples = [("Base", "Unweighted base")]*bases.shape[0]
                unweighted_bases.index = pd.MultiIndex.from_tuples(tuples)
                bases = pd.concat([bases, unweighted_bases])
            if 'Unweighted base' in df.index.get_level_values(1):
                df = df.drop('Unweighted base', level=1)
            if 'Base' in df.index.get_level_values(1):            
                df = df.drop('Base', level=1)
            df = pd.concat([bases,df])

        return df

    def combine_dataframes(self):
        return pd.concat(self.dataframes)
