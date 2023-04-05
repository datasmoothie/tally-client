from .options import Options
import json
import pandas as pd
import copy

class Presentation:

  def __init__(self, default_dataset=None, name=None, parent=None):
        self.slides = []
        self.slide_options = []
        self.default_dataset = default_dataset
        self.name = name
        self.options = Options(parent=self)
        self.parent = parent
        #self.options._set_page_setup("write_string",{"row":2, "col":0, "string":name})

  def add_slide(self, stub, banner, show='pct', table=None, options={}, dataset=None):
        """ Add a slide to the sheet

        Parameters
        ----------
        stub: string
          The varible to show on the stub (category axis in PowerPoint)
        banner: string
          The variable to show on the banner (legend in PowerPoint)
        show: string
          What the chart should show, options are: c%, r%, counts, mean
        table: string
          What to show in a table next to the chart, options are: c%, r%, counts, mean
        dataset: tally.DataSet
          Dataset to use for the crosstabs
        """
        stats = []
        ci = []
        if show=='mean':
          stats.append('mean')
        elif show=='r%':
          ci.append('r%')
        elif show=='c%':
          ci.append('c%')
        elif show=='counts':
          ci.append('counts')
        if table=='mean':
          stats.append('mean')
        elif table=='counts':
          if 'counts' not in ci:
            ci.append('counts')
        elif table=='c%':
          if 'c%' not in ci:
            ci.append('c%')
        elif table=='r%':
          if 'r%' not in ci:
            ci.append('r%')

        if show in ['r%', 'c%']:
          show_type = 'pct'
        else: 
          show_type = show

        if self.default_dataset and dataset is None:
            dataset = self.default_dataset
        crosstab = {**{"x":stub}, **{'y':banner, 'add_format_column':True, 'ci':ci, 'stats':stats}}
        df = dataset.crosstab(
            crosstabs=[crosstab]
        )
        self.slides.append(df)
        options["type"] = show_type
        if table is not None:
          options["table"] = table
        self.slide_options.append(options)

  def save_powerpoint(self, filename):
    """ Save the powerpoint to a file

    Parameters
    ----------
    filename: string
      Filename for the Powerpoint file
    """
    dataframes_payload = []
    options = []
    for slide in self.slides:
        df = slide
        df = df.replace({'null':0})
        payload = json.loads(df.to_json(orient='split'))
        payload['index_names'] = df.index.names.copy()
        payload['column_names'] = df.columns.names.copy()
        dataframes_payload.append(payload)        

    self.default_dataset.build_powerpoint_from_dataframes(filename=filename, dataframes=dataframes_payload, options=self.slide_options)

