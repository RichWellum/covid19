# covid19

Simple python code to get COVID19 numbers.

All data is pulled from: <https://github.com/CSSEGISandData/COVID-19>

Well there's a REST API too:
<https://github.com/CSSEGISandData/COVID-19/issues/124> - but it just pulls
data from the same source I am getting this from.

Data on Deaths, Confirmed cases, Recoveries and Percentage Dies are calculated
by pulling the CSV files down, and create pandas df's, summing the data up of
the last known column, which is also the latest.

![Output looks like](./output_colored.png)

To install:

```bash
    brew install pipenv
    pipenv install
```

To run infinitely:

```bash
    while true; do ./covid19.py; sleep 30; done
```

Or:

```bash
    ./covid19.sh
```
