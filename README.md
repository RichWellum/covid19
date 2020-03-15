# covid19_counter

Simple tool to display information about COVID19 and store and tweet out the
details.

Runs on a loop checking the number of Confirmed, Recovered and Deaths and also
the percentage died.

All data is pulled from: <https://github.com/CSSEGISandData/COVID-19>

User can specify the interval to check, the type of display (for small
displays), and display the record of any changes. In addition there's a test
option which allows you to enter your own data files, or make modifications.

Data on Deaths, Confirmed cases, Recoveries and Percentage Died are calculated
by pulling the CSV files down, and creating pandas df's, summing the data up
ofthe last known column, which is also the latest.

Option to Tweet the results - obviously requires a Twitter developer license
and creds populated in an auth.py file.

This is currently active: <https://twitter.com/alert_covid19>

In a seperate terminal the user can see a running history of changes:

![Output looks like](./covid_output.png)

```bash
    covid19_counter -r
```

To install on a Mac directly from github clone:

Needed: python3 and the packages (pip3 install): pandas, colorama, termcolor,
requests twython:

```bash
    brew install python3  #(or sudo apt install python3 etc)
    pip3 install pandas colorama termcolor requests twython
```

Or install from pypi:

```bash
    pip3 install covid19-counter-pkg-richwellum==<version>
    covid19_counter
```

Example running:

```bash
    RWELLUM-M-C5JH:covid19 rwellum$ covid19_counter -i 400 -h
    usage: covid19.py [-h] [-i INTERVAL] [-r] [-s] [-f] [-v] [-t]

    Grab and process the latest COVID-19 data

    optional arguments:
    -h, --help            show this help message and exit
    -i INTERVAL, --interval INTERVAL
                            interval in seconds between retrieving the data again,
                            default one hour(3600s)
    -r, --record          view a record of all changes
    -s, --split           split the display to fit smaller terminals
    -f, --force           bypass safety rails - very dangerous
    -v, --verbose         turn on verbose messages, commands and outputs
    -t, --test            run with a test file

    E.g.: ./covid19.py -i 600 -s
```
