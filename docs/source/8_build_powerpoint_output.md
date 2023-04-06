# Build PowerPoint slides
The Tally Python SDK has a flexible feature set to build PowerPoint slideshows and gives the user full, granular control over the content of the slides. The slides contain natvie Office/Excel charts, so they can be edited like any other chart created in Excel.

## The build object

We start by loading our dataset, creating a build object and add a presentation to it.

```
ds = tally.DataSet(api_key=my_token)
ds.use_spss('tests/fixtures/Example Data (A).sav')

build = tally.Build(name='client A', default_dataset=ds)

presentation = build.add_presentation('My client')
```
Then we decide what variables we want to add as charts and what we want to visualise in the charts, i.e. whether we want to show percentages, means, counts, etc.

```
presentation.add_slide(
  stub="q1", 
  banner="gender",
  show='c%',
  options={
      'chart_type':'column_stacked',
      'slide':1,
      'title':'How frequently do you do sports?'
  }
)
```
