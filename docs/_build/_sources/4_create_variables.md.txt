---
file_format: mystnb
kernelspec:
  name: python3
---
# Create variables
```{code-cell}
:tags: [remove-cell]

import os, sys
sys.path.append(os.path.abspath('../../'))
import tally
dataset = tally.DataSet(api_key=os.environ.get('tally_api_key'))
dataset.use_spss('./data/Example Data (A).sav')
```


## derive - Creating new variables

Let's say we've run a survey asking people about what sports they do. We want to create a new variable that designates people who do sports/excersize regularly and have their main fitness activity as aerobics, yoga or pilates. 

### Exploring the relevant codes

In order to do this we look at the meta data for questions `q1` and `q2b` and find the codes for aerobics, yoga, pilates and regular sporties. These are 4, 5, 6 from `q1` and 1 for `q2b`.

```{code-cell} 
:tags: [scroll-output] 

# what is your main sports activity?
dataset.meta(variable='q1')
```

```{code-cell}
:tags: [scroll-output] 
# how regularly do you excersise
dataset.meta(variable='q2b')
```


### Building the logic

We now build the logic for our new variable. Codes 1 will represent "regular sporties, mainly into yoga, aerobics or pilates" and code 2 will include non sporties and those who don't have the above sports as their main sports. We use the Tally logical system as [documented in the API.](https://tally.datasmoothie.com/#section/Selecting-responses-with-logic-operators)
```{code-cell}
cond_map = [
    (
        1, 
        "Regular sporties, mainly into yoga, aerobics or pilates", 
        { "$intersection": [{"q1":[4, 5, 6]}, {"q2b":[1]}] }
    ),
    (
        2, 
        "Non sporties, main activity not yoga, airobics, pilates", 
        {"$union":
            [
                {"$not_any":{"q2b":[1]}},
                {"$not_any":{"q1":[4,5,6]}}
            ]
        }
    )
]
```

### Creating the derived variable

Using our new logic, we create the variable with the derive method (for more details, [see the API on derive](https://tally.datasmoothie.com/#tag/Data-Processing/operation/derive)). 

```{code-cell}
dataset.derive(
    name='active_aer_yoga_pilates', 
    label='Active sporties into aerobics, yoga or pilates', 
    cond_maps=cond_map, 
    qtype="single"
)
```

Once we have created the new variable, we can sanity check it.

```{code-cell}
dataset.crosstab(x='active_aer_yoga_pilates', ci=['counts', 'c%'])
```
