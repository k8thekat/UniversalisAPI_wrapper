# Universals API Wrapper
Current todos~

### v?.?.? -
- Handle API rate limit better. (25rq/second)?
    - Query'd 500+ items and no failed returns outside of normal 404.
    - Count requests and timestamp first to last and then sleep the remainder of the second?

- Allow key to be specified for `sort_listings()`

- An item field filtering for API query in functions.
    - Consider `yarl` per @AbstractUmbra -> https://pypi.org/project/yarl/
