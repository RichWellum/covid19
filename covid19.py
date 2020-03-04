#!/usr/local/bin/python3
"""Display information about COVID19.

Runs on a loop checking the number of Confirmed, Recovered and Deaths and also
the percentage died.

All data pulled from: https://github.com/CSSEGISandData/COVID-19

User can specify the interval to check, the type of display (for small
displays), and display the record of any changes. In addition there's a test
option which allows you to enter your own data files, or make modifications.
"""

import argparse
import json
import os
import sys
from argparse import RawDescriptionHelpFormatter

import pandas as pd
import requests
from colorama import init
from termcolor import colored
from datetime import datetime
import time

# Globals used to save previous vaues when  a change occurs
PREV_CONFIRMED = 0
PREV_RECOVERED = 0
PREV_DEATHS = 0
PREV_PERCENTAGE = 0

# use Colorama to make Termcolor work
init(autoreset=True)


class AbortScriptException(Exception):
    """Abort the script and clean up before exiting."""


def parse_args():
    """Parse sys.argv and return args."""
    parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description="Grab and process the latest COVID-19 data",
        epilog="E.g.: ./covid19.py -i 600 -s",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default="3600",
        help="interval in seconds between retrieving the data again, default one hour(3600s)",
    )
    parser.add_argument(
        "-r",
        "--record",
        action="store_true",
        help="view a record of all changes in a continuously running loop",
    )
    parser.add_argument(
        "-s",
        "--split",
        action="store_true",
        help="split the display to fit smaller terminals",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="bypass safety rails - very dangerous",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="turn on verbose messages, commands and outputs",
    )
    parser.add_argument(
        "-t", "--test", action="store_true", help="run with a test file",
    )

    return parser.parse_args()


def print_banner(description):
    """
    Display a bannerized print.

    E.g.     banner("Kubernetes Join")
    """
    banner = len(description)
    if banner > 200:
        banner = 200

    # First banner
    print("\n")
    for _ in range(banner):
        print("*", end="")

    # Add description
    print("\n%s" % description)

    # Final banner
    for _ in range(banner):
        print("*", end="")
    print("\n")


def get_symbol(now, handle):
    """Calculate whether the number has increased or decreased.

    Provide a symbol showing direction of change, amount of change and whether
    to store the change

    Called each time for a different statistic so the handle is unique.
    """
    global PREV_CONFIRMED
    global PREV_RECOVERED
    global PREV_DEATHS
    global PREV_PERCENTAGE

    store_the_change = True

    # Calculate the difference and marker
    if handle == "deaths":
        if PREV_DEATHS == 0 or PREV_DEATHS == now:
            # Nothing has changed or nothing recorded (loop started)
            symbol = "<->"
            diff = 0
            store_the_change = False
        elif now > PREV_DEATHS:
            # Number of deaths has increased
            symbol = "^"
            diff = "+{}".format(now - PREV_DEATHS)
        else:
            # Number of deaths has decreased (not possible)
            symbol = "v"
            diff = "-{}".format(PREV_DEATHS - now)
            # Store new previous deaths
        PREV_DEATHS = now

    elif handle == "confirmed":
        if PREV_CONFIRMED == 0 or PREV_CONFIRMED == now:
            # Nothing has changed or nothing recorded (loop started)
            symbol = "<->"
            diff = 0
            store_the_change = False
        elif now > PREV_CONFIRMED:
            # Number of confirmed has increased
            symbol = "^"
            diff = "+{}".format(now - PREV_CONFIRMED)
        else:
            # Number of confirmed has decreased (not possible)
            symbol = "v"
            diff = "-{}".format(PREV_CONFIRMED - now)
            # Store new previous confirmed
        PREV_CONFIRMED = now

    elif handle == "recovered":
        if PREV_RECOVERED == 0 or PREV_RECOVERED == now:
            # Nothing has changed or nothing recorded (loop started)
            symbol = "<->"
            diff = 0
            store_the_change = False
        elif now > PREV_RECOVERED:
            # Number of recovered has increased
            symbol = "^"
            diff = "+{}".format(now - PREV_RECOVERED)
        else:
            # Number of recovered has decreased (not possible?)
            symbol = "v"
            diff = "-{}".format(PREV_RECOVERED - now)
            # Store new previous recovered
        PREV_RECOVERED = now

    else:  # percentage_deaths
        now = round(now, 2)
        if PREV_PERCENTAGE == 0 or PREV_PERCENTAGE == now:
            # Nothing has changed or nothing recorded (loop started)
            symbol = "<->"
            diff = 0
            store_the_change = False
        elif now > PREV_PERCENTAGE:
            # Number of percent_died_round has increased
            symbol = "^"
            diff = "+{}".format(now - PREV_PERCENTAGE)
            diff = round(float(diff), 2)
        else:
            # Number of percent_died_round has decreased
            symbol = "v"
            diff = "-{}".format(PREV_PERCENTAGE - now)
            diff = round(float(diff), 2)
            # Store new previous percent_died_round
        PREV_PERCENTAGE = now

    return (symbol, diff, store_the_change)


class Covid19:
    """Process all inputs from the user."""

    pd.options.display.max_rows = None
    pd.options.display.max_columns = None
    pd.options.display.width = None

    def __init__(self, args):
        """Initialize all variables from argparse if any."""
        self.force = args.force
        self.verbose = args.verbose
        self.record = args.record
        self.test = args.test
        self.interval = args.interval

    def get_rest(self, url):
        """Get the REST API and process the results."""
        response = requests.request("GET", url)
        response.raise_for_status()  # raise exception if invalid response
        if self.verbose:
            json_object = json.loads(response.text)
            json_formatted_str = json.dumps(json_object, indent=2)
            print(json_formatted_str)
        return response.json()

    def display_record(self):
        """Display contents of the history file.

        Create it the first time.
        """
        if self.test:
            return
        history_file = "covid19_history.dat"
        # Create the file if it's the first time and it doesn't exist
        if not os.path.exists(history_file):
            with open(history_file, "w"):
                pass
        # Printing an empty file is boring
        if os.stat(history_file).st_size == 0:
            return
        # Print the current stats
        with open(history_file, "r") as covid_file:
            print(covid_file.read())

    def download_file(self, url):
        """Download a url contents carefully."""
        if not self.test:
            local_filename = url.split("/")[-1]
            # NOTE the stream=True parameter below
            with requests.get(url, stream=True) as req:
                req.raise_for_status()
                with open(local_filename, "wb") as file:
                    for chunk in req.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            file.write(chunk)
                            # f.flush()
            return local_filename
        else:
            return url

    def display_user_inputs(self):
        """Display all user inputs in a pretty way."""
        if not self.verbose:
            return

        print_banner(
            "Force = {}, Verbose = {}, History = {}, Test = {}, Interval = {}".format(
                self.force, self.verbose, self.record, self.test, self.interval
            )
        )

    def get_csv_crunch_total(self, url):
        """Grab all the confirmed cases."""
        file = self.download_file(url)
        df_pandas = pd.read_csv(file)
        if not self.test:
            os.remove(file)

        if self.verbose:
            print(df_pandas)

        # Remove all but last (most recent) column
        df_pandas = df_pandas.iloc[:, -1]

        if self.verbose:
            print(df_pandas)

        total = df_pandas.sum()
        return total


def main():
    """Call everything."""
    args = parse_args()

    while True:
        try:
            covid19 = Covid19(args)
            covid19.display_user_inputs()

            # Purely view the statistics on a running loop
            if args.record:
                while True:
                    print_banner("Historical Data, five minute loop:")
                    covid19.display_record()
                    time.sleep(350) # Sleep 5m

            # datetime object containing current date and time
            now = datetime.now()

            if args.test:
                url = "Test_Data/Deaths.csv"
            else:
                url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
            deaths = int(covid19.get_csv_crunch_total(url))
            deaths_symbol, deaths_diff, death_store = get_symbol(deaths, "deaths")

            if args.test:
                url = "Test_Data/Confirmed.csv"
            else:
                url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
            confirmed = int(covid19.get_csv_crunch_total(url))
            confirmed_symbol, confirmed_diff, confirmed_store = get_symbol(
                confirmed, "confirmed"
            )

            if args.test:
                url = "Test_Data/Recovered.csv"
            else:
                url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
            recovered = int(covid19.get_csv_crunch_total(url))
            recovered_symbol, recovered_diff, recovered_store = get_symbol(
                recovered, "recovered"
            )

            percent_died = deaths / confirmed * 100
            percent_died_symbol, percent_died_diff, percentage_died_store = get_symbol(
                percent_died, "percent_died_round"
            )

            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            # If any change store in a file for historical purposes
            if (death_store or confirmed_store or recovered_store or percentage_died_store) and not args.test:
                covid_file = open("covid19_history.dat", "a+")
                covid_file.write(
                    "COVID19 Report({}):: Confirmed({})({}): {}, Recovered({})({}): {}, Deaths({})({}): {}, % Died({})({}): {}\n".format(
                        dt_string,
                        confirmed_symbol,
                        confirmed_diff,
                        confirmed,
                        recovered_symbol,
                        recovered_diff,
                        recovered,
                        deaths_symbol,
                        deaths_diff,
                        deaths,
                        percent_died_symbol,
                        percent_died_diff,
                        round(percent_died, 2),
                    )
                )
                covid_file.close()

            # Print header
            test_str = ""
            if args.test:
                test_str = " (Test Data)"

            interval_str = " {}s".format(args.interval)
            print()
            if args.split:
                print(
                    colored(
                        "({}{}) Covid19!{}: \n".format(
                            dt_string, interval_str, test_str
                        ),
                        "cyan",
                    )
                )
            else:
                print(
                    colored(
                        "({}{}) Covid19!:{} ".format(dt_string, interval_str, test_str),
                        "cyan",
                    ),
                    end="",
                )

            # Print Confirmed
            print(
                colored(
                    "Confirmed({})({}): {},".format(
                        confirmed_symbol, confirmed_diff, confirmed
                    ),
                    "blue",
                ),
                end="",
            )

            # Print Recovered
            print(
                colored(
                    " Recovered({})({}): {},".format(
                        recovered_symbol, recovered_diff, recovered
                    ),
                    "green",
                ),
                end="",
            )

            # Print Deaths
            print(
                colored(
                    " Deaths({})({}): {},".format(deaths_symbol, deaths_diff, deaths),
                    "red",
                ),
                end="",
            )

            # Print percentage died
            if args.split:
                print(
                    colored(
                        " % Died({})({}): {}".format(
                            percent_died_symbol,
                            percent_died_diff,
                            round(percent_died, 2),
                        ),
                        "magenta",
                    )
                )
            else:
                print(
                    colored(
                        " Percentage Died({})({}): {}".format(
                            percent_died_symbol,
                            percent_died_diff,
                            round(percent_died, 2),
                        ),
                        "magenta",
                    )
                )

            print()

            # url = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/ArcGIS/rest/services/PoolPermits/FeatureServer/query?layerDefs={'0':'Has_Pool=1 AND Pool_Permit=1','1':'Has_Pool=1 AND Pool_Permit=1'}&returnGeometry=true&f=html"
            # test = covid19.get_rest(url)
            # print(test)

        except Exception:
            print("Exception caught:")
            print(sys.exc_info())
            raise
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
