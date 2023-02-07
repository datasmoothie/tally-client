# Clean data


## `filter` - filtering data

When we want to remove certain rows from the dataset, given certain conditions, we use `filter`.

``` 
dataset.filter(alias='urban and suburban', condition={'locality':[1,2]})
```

Filter can use complex, nested logic to combine AND and OR arguments along with other logical operators. See the [API documentaion on Tally's logic operators](https://tally.datasmoothie.com/#section/Selecting-responses-with-logic-operators).

## `recode` - recoding data

Let's say a respondent said they voted for the Scottish National Party, but previously they stated that they live in Wales. The Wales statement is probably a mistake, so we want to recode our data to fix this error.

We are going to use the code for "other", which is 11, and set everyone's country to that code if their voting and the country they live in is inconsistent.

```
fix_wrong_country_mapper = {
  11: {
    '$intersection':[{'vote':[6]}, {"$not_any":{"country":[3]}}]
  }
}
dataset.recode(target='country', mapper=fix_wrong_country_mapper)
```

We use the `intersection` operator to say that anyone who said they voted for code 6 but don't live in the right country, 3, their country answer gets recoded to 11.