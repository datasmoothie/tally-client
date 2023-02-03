# Create variables


## derive - Creating new variables

Let's say we've run a survey asking people about what sports they do. We want to create a new variable that designates people who do sports/excersize regularly and have their main fitness activity as aerobics, yoga or pilates. 

### Exploring the relevant codes

In order to do this we look at the meta data for questions `q1` and `q2b` and find the codes for aerobics, yoga, pilates and regular sporties. These are 4, 5, 6 from `q1` and 1 for `q2b`.

```
# what is your main sports activity?
>>> dataset.meta(variable='q1')
```
<div style="height:240px; overflow-y:scroll;"><table style="max-width:400px;" border="1" class="dataframe">  <thead>    <tr style="text-align: left;">      <th></th>      <th>codes</th>      <th>texts</th>      <th>missing</th>    </tr>  </thead>  <tbody>    <tr>      <th>1</th>      <td>1</td>      <td>Swimming</td>      <td>None</td>    </tr>    <tr>      <th>2</th>      <td>2</td>      <td>Running/jogging</td>      <td>None</td>    </tr>    <tr>      <th>3</th>      <td>3</td>      <td>Lifting weights</td>      <td>None</td>    </tr>    <tr>      <th>4</th>      <td>4</td>      <td>Aerobics</td>      <td>None</td>    </tr>    <tr>      <th>5</th>      <td>5</td>      <td>Yoga</td>      <td>None</td>    </tr>    <tr>      <th>6</th>      <td>6</td>      <td>Pilates</td>      <td>None</td>    </tr>    <tr>      <th>7</th>      <td>7</td>      <td>Football (soccer)</td>      <td>None</td>    </tr>    <tr>      <th>8</th>      <td>8</td>      <td>Basketball</td>      <td>None</td>    </tr>    <tr>      <th>9</th>      <td>9</td>      <td>Hockey</td>      <td>None</td>    </tr>    <tr>      <th>10</th>      <td>96</td>      <td>Other</td>      <td>None</td>    </tr>    <tr>      <th>11</th>      <td>98</td>      <td>I regularly change my fitness activity</td>      <td>None</td>    </tr>    <tr>      <th>12</th>      <td>99</td>      <td>Not applicable - I don\'t exercise</td>      <td>None</td>    </tr>  </tbody></table></div>

<br/>
```
# how regularly do you excersise
>>> dataset.meta(variable='q2b')
```
<table style="" border="1" class="dataframe">  <thead>    <tr style="text-align: left;">      <th></th>      <th>codes</th>      <th>texts</th>      <th>missing</th>    </tr>  </thead>  <tbody>    <tr>      <th>1</th>      <td>1</td>      <td>Regularly</td>      <td>None</td>    </tr>    <tr>      <th>2</th>      <td>2</td>      <td>Irregularly</td>      <td>None</td>    </tr>    <tr>      <th>3</th>      <td>3</td>      <td>Never</td>      <td>None</td>    </tr>  </tbody></table>
<br/>

### Building the logic

We now build the logic for our new variable. Codes 1 will represent "regular sporties, mainly into yoga, aerobics or pilates" and code 2 will include non sporties and those who don't have the above sports as their main sports. We use the Tally logical system as [documented in the API.](https://tally.datasmoothie.com/#section/Selecting-responses-with-logic-operators)
```
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

```
dataset.derive(
    name='active_aer_yoga_pilates', 
    label='Active sporties into aerobics, yoga or pilates', 
    cond_maps=cond_map, 
    qtype="single"
)
```

Once we have created the new variable, we can sanity check it.

```
>>> dataset.crosstab(x='active_aer_yoga_pilates')
```
<table border="1" class="dataframe">  <thead>            <tr>      <th>Question</th>      <th>Values</th>      <th></th>    </tr>  </thead>  <tbody>    <tr>      <th rowspan="3" valign="top">Active sporties into aerobics, yoga or pilates</th>      <th>Base</th>      <td>8255.0</td>    </tr>    <tr>      <th>Regular sporties, mainly into yoga, aerobics or pilates</th>      <td>339.0</td>    </tr>    <tr>      <th>Non sporties, main activity not yoga, airobics, pilates</th>      <td>7916.0</td>    </tr>  </tbody></table>