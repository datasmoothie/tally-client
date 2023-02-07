---
file_format: mystnb
kernelspec:
  name: python3
---
# Explore data

```{code-cell}
:tags: [remove-cell]

import os, sys
sys.path.append(os.path.abspath('../../'))
import tally
dataset = tally.DataSet(api_key=os.environ.get('tally_api_key'))
dataset.use_spss('./data/Example Data (A).sav')
```
 
Once our data is loaded, we can explore what variables it has and the meta data for the variables. We assume that the data [has been loaded](../1_load_data) into a variable called `dataset`. For more information on the API endpoints used in these examples, refer to the [Tally API documentation](https://tally.datasmoothie.com).

## `variables` - listing available variables by type 

Use the [variables](https://tally.datasmoothie.com/#tag/Data-Processing/operation/variables) method to get a list of variables. It returns a dictionary with the keys keys `single`, `delimited set`, `array`, `int`, `float`, `string`, `date`. These all have a list of strings that are the names of variables.

```{code-cell}
:tags: [scroll-output] 

dataset.variables()
```

## `meta` - explore answer labels and codes 

Use the [meta](https://tally.datasmoothie.com/#tag/Data-Processing/operation/meta) method to explore answer codes and labels.

```{code-cell}
:tags: [scroll-output] 
dataset.meta(variable='q1')
```


## Other methods to explore data

Other methods to explore the data include **get_variable_text**, **find**, **values** and other methods in the [DataSet class](api_dataset). 

```{code-cell}
dataset.get_variable_text(name='locality')
```

```{code-cell}
:tags: [scroll-output] 
dataset.find(str_tags=['q2'])
```

```{code-cell}
dataset.values(name='locality')
```


## Pandas dataframe

The data can also be accessed as a pandas dataframe.

```{code-cell}
:tags: [scroll-output] 
df = dataset.get_dataframe()
df.head()
```

