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
        self.tables = []

    def add_table(self, name=None, banner='@'):
        t = Table(banner=banner, default_dataset=self.default_dataset)
        self.tables.append(t)
        return t

    def save_excel(self, filename):
        payload = json.loads(result.to_json(orient='split'))
        payload['index_names'] = result.index.names.copy()
        payload['column_names'] = result.columns.names.copy()
        ds.build_excel_from_dataframes(filename='seperate_bases.xlsx', dataframes=[payload])
    
class Table:
    def __init__(self, banner='@', default_dataset=None):
        self.banner = banner
        self.dataframes = []
        self.default_dataset = default_dataset

    def add_data(self, stub, options={}, dataset=None):
        if self.default_dataset and dataset is None:
            dataset = self.default_dataset
        crosstab = {**stub, **{'y':self.banner, 'add_format_column':True}}
        df = dataset.crosstab(
            crosstabs=[crosstab]
        )
        df = self.apply_options(df, options)
        self.dataframes.append(df)

    def apply_options(self, df, options):
        if 'base' in options:
            df = self.apply_base_options(df, options['base'])
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
