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

Can also be run continuously with 'watch -d ./covid19.py'
