# covid19

Simple but somewhat morbid tool to display information about COVID19.

Runs on a loop checking the number of Confirmed, Recovered and Deaths and also
the percentage died.

All data is pulled from: <https://github.com/CSSEGISandData/COVID-19>

User can specify the interval to check, the type of display (for small
displays), and display the record of any changes. In addition there's a test
option which allows you to enter your own data files, or make modifications.

Data on Deaths, Confirmed cases, Recoveries and Percentage Died are calculated
by pulling the CSV files down, and creating pandas df's, summing the data up
ofthe last known column, which is also the latest.

![Output looks like](./covid_output.png)

To install on a Mac:

```bash
    cd covid19 # cd to the directory
    brew install pipenv
    pipenv install # Seems temperamental - so use manual steps below if needed
```

Otherwise you need python3 and the packages (pip3 install): pandas, colorama,
termcolor, requests:

```bash
    brew install python3  #(or sudo apt install python3 etc)
    pip3 install pandas colorama termcolor requests
```

Example running:

```bash
    RWELLUM-M-C5JH:covid19 rwellum$ ./covid19.py -i 400 -h
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
