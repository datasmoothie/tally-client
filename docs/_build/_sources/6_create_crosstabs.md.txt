---
file_format: mystnb
kernelspec:
  name: python3
---
# Create crosstabs


## Introduction
Tally's `crosstab` method supports a variety of options and can be used both in a Jupyter Notebook environment and to produce Excel tables. Here we will cover how the method works and what options it supports, and in the next section we will show how it can be used to generate Excel tables.

Using the crosstab method in a Jupyter Notebook, as opposed to using it to populate an Excel file, is useful for verifying the data processing work we are doing and for sanity and quality checks.

## Running a basic crosstab
Tally's crosstab method is used to run crosstabs (see the [API reference on crosstab](https://tally.datasmoothie.com/#tag/Aggregations/operation/crosstab) for full details).


```{code-cell}
:tags: [remove-cell]

import os, sys
sys.path.append(os.path.abspath('../../'))
import tally
dataset = tally.DataSet(api_key=os.environ.get('tally_api_key'))
dataset.use_spss('./data/Example Data (A).sav')
```

```{code-cell}
dataset.crosstab(x='q2b', y='gender')
```

The default value displayed in the table cells are counts. We can decide whether we want to display counts, column percentages (c%) or both with the `ci` parameter. For a full list of parameters, consult the [DataSet class documentation](api_dataset)

```{code-cell}
dataset.crosstab( x='q2b', y='gender', ci=['counts', 'c%'])
```

## Intepreting significance test results

We can test for significance using column proportion tests by adding the parameter `sig_level`.

```{code-cell}
dataset.crosstab(x='q2b', y='locality', ci=['c%'], sig_level=[0.05])
```
Each answer has its own letter to identify it, e.g. "Central Business District" is A, "Urban" is B. The test results are shown by each answer, and if a letter for a column shows up, it means that the current column is significantly higher than the column indicated by the letter. For example, people who live in central business districts and in urban locations (Test-IDs A and B) are significantly liklier to excersise regularly than those in Remote locations (Test-ID E).


## Adding descriptive statistics to crosstabs

We can add descriptive statistics to crosstabs with the parameter 'stats'.

```{code-cell}
dataset.crosstab(x='q14r01c01', y='locality', ci=['c%'], stats=['mean'], sig_level=[0.05])
```

Here we have added `mean` to the results, and as we can see, it gets tested for significance as well as the other answers.

## `filter` - selecting cuts from your data
We can select subsets of the data to work with for a particular crosstab, instead of filtering the whole dataset like we did in [the section on cleaning](../3_clean_data), with the parameter `f`.


```{code-cell}
dataset.crosstab(x='q14r06c03', y='locality', f={'gender':[1]})
```


