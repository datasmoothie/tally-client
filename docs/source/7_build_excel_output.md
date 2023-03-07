# Build Excel tables
The Tally Python SDK has a flexible feature set to build large Excel data tables and gives the user full, granular control over the content of the tables.


![Tally supports building large Excel data files and granular control](_static/assets/images/documentation/screenshots/excel-tables-with-toc.png)

## The build object
Tally implements an object called `build` which represents each build of outputs. Each build has a list of sheets and each sheet has a list of tables.

![Tally supports building large Excel data files and granular control](_static/assets/images/documentation/diagrams/excel-build-diagram.png)

If there are more than one sheets in a build, a table of contents is automatically created. A logo can also be included in the build and font familyi and font sizes can be set.

```
build = tally.Build(
    name="Sport survey", 
    subtitle="Annual research conducted by agency X",
    default_dataset=dataset,
    table_of_contents=True,
    logo='./images/datasmoothie-logo.png'
)
```

## Adding sheets, tables and saving the Excel file
Once we have created the `build`, we can add sheets and tables. Every sheet must belong to a build and every table must belong to a sheet.

```
sheet = build.add_sheet(banner='Wave')
sheet.name = 'Waves'

sheet.add_table(stub={"x":"q1"})
sheet.add_table(stub={"x":"q2"})
sheet.add_table(stub={"x":"q3"})
```

### Adding multiple sheets
We can use a `for` loop to add multiple sheets to our build.
```
for stub in stub_vars:
    sheet = build.add_sheet(banner=banner_vars)
    sheet.name = dataset.get_variable_text(name=stub)
    sheet.add_table(stub={"x":stub})

```


### Creating the Excel document
Once we've added our sheets and tables to the build, we can create the Excel document.

```
build.save_excel('client_results.xlsx')
```

A new file will get saved in the location your python script is located, called client_results.xlsx. 


## Setting build options on a build, sheet, and table level
Most data-specific and visual options can be set on a build, sheet or table level. For example, the entire build could use a certain variable for weighting, certain sheets can be tested for significance and certain tables could show descriptive statistics.

### Setting options on a build level
Options set on the build level will apply to every table in every sheet, unless otherwise specified. Sheet options override build options and table options override both.

```
build.options.set_weight('weight_a')
build.options.set_ci(['c%', 'counts'])
```
The above will weight all results with the variable `weight_a` and only show both percentages and counts in all tables.

### Setting options on a sheet level
Options can be set on a per-sheet level. If we've already set certain options on a build level, these will be overridden by sheet-level options.

```
build.options.set_stats(['mean'])
sheet1 = build.add_sheet(name="Q1 With means", banner=["locality"])
sheet1.add_table(stub={'x':'q1'})
sheet2 = build.add_sheet(name="Q1 With means and standard deviation", banner=["locality"])
sheet2.options.set_stats(['mean', 'stddev'])
sheet2.add_table(stub={'x':'q2'})
```

In the above, `sheet1` and will have mean calculations included in its tables, whereas `sheet2` will have both means and standard deviation. Every other sheet added will have mean calculated, but not standard deviation.


### Setting options on a table level
Options can also be set on a table-level, if there's only one table in a sheet that should have certain data included.

```
build.options.set_weight('weight_a')
sheet = build.add_sheet(name="Q1", banner=["locality"])
sheet.add_table(stub={'x':'q1'})
sheet.add_table(stub={'x':'q2'}, options={'weight':'weight_b'})
```
In the above, every table in the sheet will be weighted with the weight variable `weight_a` except that last one, which will be weighted with `weight_b`.


## Deciding what data to include
Tally Excel builds support all the data you would expect to be able to include, such as

- Counts
- Percentages
- Bases (weighted and unweighted)
- Significance testing
- Descriptive statistics (mean, standard deviation, etc.)

All of the above are options we send to the `crosstab` method and the options available are shown in the [API Reference for the crosstab method](https://tally.datasmoothie.com/#tag/Aggregations/operation/crosstab).

### Significance testing
Significance testing is done by adding an alpha paremeter (or significance level parameter). This is often 0.05 or 0.10. This can be done on a build, sheet or table level.

```
# build level
build.options.set_sig_test_levels(0.05)
# sheet level
build.options.set_sig_test_levels(0.05)
# table level
sheet.add_table(stub={'x':'q1', 'sig_level':[0.05]})
```


### Descriptive statistics
Descriptive statistics are added to tables with the `set_stats` options for builds and sheets, and the `stats` option for tables.

```
build.options.set_stats(['mean'])
sheet10.options.set_stats(['mean', 'stddev'])
sheet10.add_table(stub={'x':'q1', 'stats':['mean', 'stddev']})
```

Available statistics are 
 - mean: Mean,
 - min: Min,
 - max: Max,
 - median: Median,
 - var: Sample variance,
 - varcoeff: Coefficient of variation,
 - stddev: Std. dev,
 - sem: Std. err. of mean,
 - sum: Total Sum,
 - lower_q: Lower quartile,
 - upper_q: Upper quartile'

### Annotations
Tables can include annotations that show

- what variable was used as a weight
- how the base was selected (e.g. Location: London)
- the alpha parameter in the significance testing

```
build.options.set_annotations(True)
sheet.options.set_annotations(True)
```

## Controlling visuals
Users can set formatting for result types in a table (percentages, counts, stats) and these can be set on the entire table or on a column-by-column basis. The following are the most common commands.

- `set_format`
- `set_answer_format`
- `set_column_format_for_type`
- `set_base_labels`
- `set_banner_border`
- `set_base_position`

For example:
```
# make all descriptive statistics appear in a certain colour
sheet.options.set_format('stats', {"font_color":"98B4DF"})
# set the format for all base rows, making them bold, with a border and in a color
build.options.set_format('base', {'bold':True, 'border': 1, 'border_color':'efefef'})
# Make the base in column 1 always be bold
sheet.options.set_column_format_for_type('base', 1, {"bold":True})
```

For more information about each function, see [the section about the Build API](api_build).

### The format dictionary
Formats are controlled by contstructing a format dictionary. This is a dictionary with keys that indicate what format should be changed and values that indicate how the formats should be set. For example

```
{'bold': True, 'font_color':efefef, 'align':'left}
```

For a list of formatting options used to build the formatting dictionary, see the <a href="#formatting-options">formatting options list</a>

### Adding a header/title to a table

Options can be set on a table level as well, and this can be used to add a header to the table.

```
sheet.add_table(
    stub={...}, 
    options={
        'title':{'text':'This is my title', 'format':{'bold':True, 'font_color':'#ebebeb'}}
    }
)

```

For the formatting options available for the header, see the <a href="#formatting-options">formatting options list</a>.


## Formatting options
The look and format of every question, label and data table can be set to get the right look and feel.

<table border="0" class="table">
<colgroup>
<col width="15%">
<col width="22%">
<col width="27%">
<col width="37%">
</colgroup>
<thead valign="bottom">
<tr class="row-odd"><th class="head">Category</th>
<th class="head">Description</th>
<th class="head">Property</th>
<th class="head">Example</th>
</tr>
</thead>
<tbody valign="top">
<tr class="row-even"><td>Font</td>
<td>Font type</td>
<td><code class="docutils literal notranslate"><span class="pre">'font_name'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">"Arial"</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Font size</td>
<td><code class="docutils literal notranslate"><span class="pre">'font_size'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">12</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Font color</td>
<td><code class="docutils literal notranslate"><span class="pre">'font_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Bold</td>
<td><code class="docutils literal notranslate"><span class="pre">'bold'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Italic</td>
<td><code class="docutils literal notranslate"><span class="pre">'italic'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Underline</td>
<td><code class="docutils literal notranslate"><span class="pre">'underline'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Strikeout</td>
<td><code class="docutils literal notranslate"><span class="pre">'font_strikeout'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Super/Subscript</td>
<td><code class="docutils literal notranslate"><span class="pre">'font_script'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">1 = Superscript, 2 = Subscript</span></code></td>
</tr>
<tr class="row-even"><td>Number</td>
<td>Numeric format</td>
<td><code class="docutils literal notranslate"><span class="pre">'num_format'</span></code></td>
<td><a class="reference internal" href="#set_num_format" title="set_num_format"><code class="xref py py-func docutils literal notranslate"><span class="pre"><a href="https://xlsxwriter.readthedocs.io/format.html#set_num_format">See xlsxwriter docs</a></span></code></a></td>
</tr>
<tr class="row-odd"><td>Protection</td>
<td>Lock cells</td>
<td><code class="docutils literal notranslate"><span class="pre">'locked'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-odd"><td>Alignment</td>
<td>Horizontal align</td>
<td><code class="docutils literal notranslate"><span class="pre">'align'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">left, 
center,
right,<br/>
fill,
justify,
center_across,<br/>
distributed</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Vertical align</td>
<td><code class="docutils literal notranslate"><span class="pre">'valign'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">
top,
vcenter,
bottom,<br/>
vjustify,
vdistributed</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Rotation</td>
<td><code class="docutils literal notranslate"><span class="pre">'rotation'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">45</span></code> (degrees)</td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Text wrap</td>
<td><code class="docutils literal notranslate"><span class="pre">'text_wrap'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Justify last</td>
<td><code class="docutils literal notranslate"><span class="pre">'text_justlast'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Center across</td>
<td><code class="docutils literal notranslate"><span class="pre">'center_across'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Indentation</td>
<td><code class="docutils literal notranslate"><span class="pre">'indent'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">1,2 </span></code>(indent level)</td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Shrink to fit</td>
<td><code class="docutils literal notranslate"><span class="pre">'shrink'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">True/False</span></code></td>
</tr>
<tr class="row-even"><td>Pattern</td>
<td>Cell pattern</td>
<td><code class="docutils literal notranslate"><span class="pre">'pattern'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">0-18</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Background color</td>
<td><code class="docutils literal notranslate"><span class="pre">'bg_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Foreground color</td>
<td><code class="docutils literal notranslate"><span class="pre">'fg_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-odd"><td>Border</td>
<td>Cell border</td>
<td><code class="docutils literal notranslate"><span class="pre">'border'</span></code></td>
<td><a class="reference internal" href="https://xlsxwriter.readthedocs.io/format.html#set_border" title="set_border"><code class="xref py py-func docutils literal notranslate"><span class="pre">See xlsxwwriter docs</span></code></a></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Bottom border</td>
<td><code class="docutils literal notranslate"><span class="pre">'bottom'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">1,2,3</span></code> (see docs for set_border)</td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Top border</td>
<td><code class="docutils literal notranslate"><span class="pre">'top'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">1,2,3, ...</span></code> (see docs for set_border)</td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Left border</td>
<td><code class="docutils literal notranslate"><span class="pre">'left'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">1,2,3, ...</span></code> (see docs for set_border)</td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Right border</td>
<td><code class="docutils literal notranslate"><span class="pre">'right'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">1,2,3, ...</span></code> (see docs for set_border)</td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Border color</td>
<td><code class="docutils literal notranslate"><span class="pre">'border_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Bottom color</td>
<td><code class="docutils literal notranslate"><span class="pre">'bottom_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Top color</td>
<td><code class="docutils literal notranslate"><span class="pre">'top_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-odd"><td>&nbsp;</td>
<td>Left color</td>
<td><code class="docutils literal notranslate"><span class="pre">'left_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
<tr class="row-even"><td>&nbsp;</td>
<td>Right color</td>
<td><code class="docutils literal notranslate"><span class="pre">'right_color'</span></code></td>
<td><code class="xref py py-func docutils literal notranslate"><span class="pre">#efefef</span></code></td>
</tr>
</tbody>
</table>

