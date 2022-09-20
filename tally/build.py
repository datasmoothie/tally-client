import pandas as pd
import json

class Build:
    """
    A class that gathers together crosstabs a user wants to use to build Excel, Powerpoint or Datasmoothie dashboards output. 

    Parameters
    ----------
      name: string
        Name for the dataset
    """

    def __init__(self, name=None, default_dataset=None):
        self.name = name
        self.default_dataset = default_dataset
        self.sheets = []

    def add_sheet(self, name=None, banner='@'):
        sheet = Sheet(banner=banner, default_dataset=self.default_dataset)
        self.sheets.append(sheet)
        return sheet

    def save_excel(self, filename):
        dataframes_payload = []
        for sheet in self.sheets:
            df = sheet.combine_dataframes()
            payload = json.loads(df.to_json(orient='split'))
            payload['index_names'] = df.index.names.copy()
            payload['column_names'] = df.columns.names.copy()
            dataframes_payload.append(payload)

        self.default_dataset.build_excel_from_dataframes(filename=filename, dataframes=dataframes_payload)
    
class Sheet:
    def __init__(self, banner='@', default_dataset=None):
        self.banner = banner
        self.dataframes = []
        self.default_dataset = default_dataset
        self.options = {}
        self.table_options = {}

    def add_table(self, stub, options={}, dataset=None):
        if self.default_dataset and dataset is None:
            dataset = self.default_dataset
        crosstab = {**stub, **{'y':self.banner, 'add_format_column':True}}
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
        return df

    def apply_table_format_options(self, df, options):
        if 'base' in options:
            new_format = {0:{'format':options['base']}}
            df = self.set_format_for_type(df, 'base', new_format)
        return df

    def set_format_for_type(self, df, type, format):
        """ Method to add/alter format json per cell or per question type.

        Parameters:
            type (string): can be base, count, percentage or any type returned by the Tally API
            format (dict): what gets merged with cell_format
        """
        new_format = format
        location = df[df['FORMAT'].str.contains(f'\"type\": \"{type}\"')].index
        if len(location) == 0:
            location = df[df['FORMAT'].str.contains(f'\"original_type\": \"{type}\"')].index
        df.at[location, ('FORMAT',)] = df.loc[location]['FORMAT'].apply(lambda x, new_format: json.dumps({**json.loads(x), **new_format}), args=[new_format])
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
