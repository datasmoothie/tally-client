# Building a survey data pipeline

A survey data pipeline connects to a database, either directly to a survey platform like Unicom, Forsta (Confirmit, Decipher), Qualtrics, or a data warehouse. It can also read a file as it is dropped onto an FTP server.

The pipeline defines data processing tasks such as cleaning, weighting, and creating variables, and finally it build outputs.

![Survey data pipeline diagram](/assets/images/documentation/diagrams/Survey-data-pipeline.png)

## Tally as a survey data pipeline

Tally can perform every step of the survey data pipeline, and it also allows users to use software testing to make sure the survey data being collected adheres to the standards required, from an integrity and consistency standpoint.

The typical steps of a survey data pipeline involve the following:

1. [Loading/exctacting data](1_load_data)
1. [Clean](3_clean_data)
1. [Create variables](4_create_variables)
1. [Weight](5_weight_data)
1. [Build Excel tables](7_build_excel_output)
