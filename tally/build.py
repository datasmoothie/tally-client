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

    def add_data(self, stub, options={}, dataset=None):
        if self.default_dataset and dataset is None:
            dataset = self.default_dataset
        crosstab = {**stub, **{'y':self.banner, 'add_format_column':True}}
        df = dataset.crosstab(
            crosstabs=[crosstab]
        )
        options = {**self.table_options, **options}
        df = self.apply_table_options(df, options)
        df = self.apply_sheet_options(df, self.options)
        self.dataframes.append(df)

    def apply_table_options(self, df, options):
        if 'base' in options:
            df = self.apply_base_options(df, options['base'])
        return df

    def apply_sheet_options(self, df, options):
        if 'pull_base_up' in options:
            if options['pull_base_up'] == False:
                df['FORMAT'] = df['FORMAT'].str.replace('base','counts')
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
