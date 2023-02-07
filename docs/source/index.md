---
sd_hide_title: true
---
# Tally SDK documentation


::::{grid} 2
:reverse:

:::{grid-item}
:columns: 4
:class: sd

<img src="https://www.datasmoothie.com/static/assets/img/Tally-robot-illustration.svg" />

:::

:::{grid-item}
:columns: 8
:class: sd-fs-3
Use Python to integrate multiple survey data platforms, perform data processing tasks, and build Excel tables, Powerpoint presentations and dashboards.


```{button-ref} Quick_Start
:ref-type: doc
:color: primary
:class: sd-rounded-pill float-left

:::
::::

```{toctree}
:hidden:

Quick_Start
```

```{toctree}
:caption: The pipeline
:hidden:

pipeline_intro
1_load_data
2_explore_data
3_clean_data
4_create_variables
5_weight_data
6_create_crosstabs
7_build_excel_output
```

```{toctree}
:caption: API Reference
:hidden:

the_api
api_build
api_dataset
```

```{toctree}
:hidden:

terminology
```

Tally is a tool for survey and market research data processing, analysis, and publishing. It allows users to combine multiple survey data platforms, run data processing tasks such as cleaning, weighting, merging data and creating new variables. It also produces Excel data tables, Powerpoint files and interactive dashboards.

Tally is composed of two parts:

- A RESTful API
- A Python client library for the API

Because Tally is based on an API, it supports R, JavaScript and any other programming language. It can also be plugged into a data warehouse pipeline, where it can both be used as an ETL layer and an OLAP layer for survey data.

Creating a survey data pipeline
---

::::{grid} 1 2 2 3
:margin: 4 4 0 0
:gutter: 4

:::{grid-item-card} {octicon}`rocket` Quick start
:link: Quick_Start
:link-type: doc

Quickstart guide to get started using Tally.
:::

:::{grid-item-card} {octicon}`upload` Load/extract data
:link: 1_load_data
:link-type: doc

Load an SPSS file or connect to survey data platform.
:::

:::{grid-item-card} {octicon}`paintbrush` Clean data
:link: 3_clean_data
:link-type: doc

Clean data with advanced filtering and recoding.
:::

:::{grid-item-card} {octicon}`plus` Create variables
:link: 4_create_variables
:link-type: doc

Create new variables by deriving logic from other variables.
:::

:::{grid-item-card} {octicon}`verified` Weight data
:link: 5_weight_data
:link-type: doc

Weight data with the RIM/RAKE algorithm.
:::

:::{grid-item-card} {octicon}`table` Create crosstabs
:link: 6_create_crosstabs
:link-type: doc

Explore your results, significance tests, and descriptive statistics.
:::

:::{grid-item-card} {octicon}`file` Build Excel tables
:link: 7_build_excel_output
:link-type: doc

Build Excel outputs with fine grained control over outputs.
:::



::::

Reference
---

- [API Reference](the_api)
- [Building outputs](api_build)
- [Data processing with the DataSet class](api_dataset)
