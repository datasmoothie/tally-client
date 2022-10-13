from .options import Options
import json
import pandas as pd
import copy

class Sheet:
    def __init__(self, banner='@', default_dataset=None, name=None):
        self.banner = banner
        self.tables = []
        self.default_dataset = default_dataset
        self.name = name
        self.options = Options()

    def get_name(self):
        if self.name is not None:
            return self.name
        else:
            if len(self.dataframes)>0:
                name = self.dataframes[0].index.get_level_values(0)[0]
                if name == 'Base' or name == 'Unweighted base':
                    #check the format column if this is either a base or space row
                    return self.dataframes[0][~self.dataframes[0]['FORMAT'].str.contains('base|spacer', regex=True, case=False)].index[0][0]                       
                else:
                    return name
            else:
                return ""

    def add_table(self, stub, options={}, dataset=None):
        if self.default_dataset and dataset is None:
            dataset = self.default_dataset
        crosstab = {**{**self.options.table_options['stub'], **stub}, **{'y':self.banner, 'add_format_column':True}}
        df = dataset.crosstab(
            crosstabs=[crosstab]
        )
        self.tables.append({"dataframe":df, "options":options})

    def paint_dataframes(self):
        for table in self.tables:
            options = {**self.options.table_options, **table['options']}
            df = table['dataframe']
            # the format column should always have a cell_options key
            df['FORMAT'] = df['FORMAT'].apply(lambda x: json.dumps({**json.loads(x), **{'cell_format':{}}}))
            df = self.apply_table_options(df, options)
            df = self._append_row_to_dataframe(df)
            table['dataframe'] = df


    def apply_table_options(self, df, options):
        if 'base' in options:
            df = self.apply_base_options(df, options['base'])
        if 'base_label' in options:
            df = df.rename(index={'Base':options['base_label']}, level=1)
        if 'format' in options:
            df = self.apply_table_format_options(df, options['format'])
        if 'row_format' in options:
            df = self.set_row_format(df, options['row_format'])
        if 'banner_border' in options:
            df = self.add_banner_border(df)
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

    def _set_column_format(self, df, col_index, format):
        def apply_column_format(x, col_index, new_format):
            current_format = json.loads(x)
            for i in col_index:
                if str(i) in current_format['cell_format']:
                    current_format['cell_format'][str(i)]['format'] = {**current_format['cell_format'][str(i)]['format'], **new_format}
                else:
                    current_format['cell_format'][str(i)] = {'format':new_format}
            return json.dumps(current_format)
        # users can send int and lists
        if type(col_index) != list:
            col_index = [col_index]
        for row in list(range(df.shape[0])):
            if 'spacer' not in json.loads(df.iloc[row, -1]):
                df.iat[row, -1] = apply_column_format(df.iloc[row, -1], col_index, format)
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
        loc_row_index = list(location.get_level_values(1))
        for row in loc_row_index:
            df.iat[row, -1] = apply_format(df.iloc[row,-1], new_format)
        df.index = old_index
        df.index = df.index.set_names(['Question', 'Values'])
        return df

    def add_banner_border(self, df):
        all_questions = df.columns.to_frame().index.to_series().reset_index()['Question']
        # find location of first unique question (this is the far left column in each subframe)
        all_questions = list(all_questions.drop_duplicates().iloc[:-1].index)
        # the question column is col 0 and we don't count that
        if 0 in all_questions:
            all_questions.remove(0)
        all_questions = [i+1 for i in all_questions]
        self._set_column_format(df, all_questions, {'left':1})
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
            bases = self._append_row_to_dataframe(bases)
            df = pd.concat([bases,df])

        return df

    def _append_row_to_dataframe(self, df):
        last_question = df.index.get_level_values(0)[-1]
        mi = pd.MultiIndex.from_tuples([(last_question, ' ')])
        empty_row_df = pd.DataFrame(columns=df.columns, data=[['']*df.shape[1]], index=mi)
        empty_row_df.iloc[-1, -1] = '{"type":"counts", "spacer":true, "cell_format":{}}'
        df = pd.concat([df, empty_row_df])
        return df

    def build_dataframes(self, build_options=None):
        if len(self.tables) == 0:
            raise Exception("Sheet {} has no tables".format(self.name))
        self.options.merge(build_options)
        self.options.set_question_format('percentage', {'text_wrap':True})
        self.options.set_question_format('counts', {'text_wrap':True})

        self.paint_dataframes()
        dataframes = [i['dataframe'] for i in self.tables]
        return pd.concat(dataframes)
