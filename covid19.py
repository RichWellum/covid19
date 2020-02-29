#!/usr/local/bin/python3
"""Grab some info about covid19.

All data pulled from: https://github.com/CSSEGISandData/COVID-19

Recommend doing: 'watch -d ./covid19.py'
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

# use Colorama to make Termcolor work
init(autoreset=True)


class AbortScriptException(Exception):
    """Abort the script and clean up before exiting."""


def parse_args():
    """Parse sys.argv and return args."""
    parser = argparse.ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description="Grab some COVID-19 datan",
        epilog="E.g.: ./covid19",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Bypass safety rails - very dangerous",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="turn on verbose messages, commands and outputs",
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


def download_file(url):
    """Download a url contents carefully."""
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


class Covid19:
    """Process all inputs from the user."""

    pd.options.display.max_rows = None
    pd.options.display.max_columns = None
    pd.options.display.width = None

    def __init__(self, args):
        """Initialize all variables from argparse if any."""
        self.force = args.force
        self.verbose = args.verbose
        self.previous_confirmed = 0
        self.previous_recovered = 0
        self.previous_deaths = 0
        self.previous_percentage = 0

    def get_symbol(self, now, handle):
        """Calculate whether the number has increased or decreased.

        Provide a symbol showing direction of change.

        Called each time for a different statistic so the handle is unique.
        """
        # Calculate the difference and marker
        if handle == "deaths":
            if self.previous_deaths == 0 or self.previous_deaths == now:
                # Nothing has changed or nothing recorded (loop started)
                symbol = "<->"
                diff = 0
            elif now > self.previous_deaths:
                # Number of deaths has increased
                symbol = "^"
                diff = "+{}".format(now - self.previous_deaths)
                self.previous_deaths = now
            else:
                # Number of deaths has decreased (not possible)
                symbol = "v"
                diff = "-{}".format(self.previous_deaths - now)
                # Store new previous deaths
                self.previous_deaths = now

        elif handle == "confirmed":
            if self.previous_confirmed == 0 or self.previous_confirmed == now:
                # Nothing has changed or nothing recorded (loop started)
                symbol = "<->"
                diff = 0
            elif now > self.previous_confirmed:
                # Number of confirmed has increased
                symbol = "^"
                diff = "+{}".format(now - self.previous_confirmed)
                self.previous_confirmed = now
            else:
                # Number of confirmed has decreased (not possible)
                symbol = "v"
                diff = "-{}".format(self.previous_confirmed - now)
                # Store new previous confirmed
                self.previous_confirmed = now

        elif handle == "recovered":
            if self.previous_recovered == 0 or self.previous_recovered == now:
                # Nothing has changed or nothing recorded (loop started)
                symbol = "<->"
                diff = 0
            elif now > self.previous_recovered:
                # Number of recovered has increased
                symbol = "^"
                diff = "+{}".format(now - self.previous_recovered)
                self.previous_recovered = now
            else:
                # Number of recovered has decreased (not possible?)
                symbol = "v"
                diff = "-{}".format(self.previous_recovered - now)
                # Store new previous recovered
                self.previous_recovered = now

        else:  # percentage_deaths
            if self.previous_percentage == 0 or self.previous_percentage == now:
                # Nothing has changed or nothing recorded (loop started)
                symbol = "<->"
                diff = 0
            elif now > self.previous_percentage:
                # Number of percent_died_round has increased
                symbol = "^"
                diff = "+{}".format(now - self.previous_percentage)
                self.previous_percentage = now
            else:
                # Number of percent_died_round has decreased
                symbol = "v"
                diff = "-{}".format(self.previous_percentage - now)
                # Store new previous percent_died_round
                self.previous_percentage = now

        return (symbol, diff)

    def get_rest(self, url):
        """Get the REST API and process the results."""
        response = requests.request("GET", url)
        response.raise_for_status()  # raise exception if invalid response
        if self.verbose:
            json_object = json.loads(response.text)
            json_formatted_str = json.dumps(json_object, indent=2)
            print(json_formatted_str)
        return response.json()

    def display_user_inputs(self):
        """Display all user inputs in a pretty way."""
        if not self.verbose:
            return

        print_banner("Force = {}, Verbose = {}".format(self.force, self.verbose,))

    def get_csv_crunch_total(self, url):
        """Grab all the confirmed cases."""
        file = download_file(url)
        df_pandas = pd.read_csv(file)
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

            # datetime object containing current date and time
            now = datetime.now()

            url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
            deaths = int(covid19.get_csv_crunch_total(url))
            deaths_symbol, deaths_diff = covid19.get_symbol(deaths, "deaths")

            url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
            confirmed = int(covid19.get_csv_crunch_total(url))
            confirmed_symbol, confirmed_diff = covid19.get_symbol(
                confirmed, "confirmed"
            )

            url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
            recovered = int(covid19.get_csv_crunch_total(url))
            recovered_symbol, recovered_diff = covid19.get_symbol(
                recovered, "recovered"
            )

            percent_died = deaths / confirmed * 100
            percent_died_round = str(round(percent_died, 2))
            percent_died_round_symbol, percent_died_round_diff = covid19.get_symbol(
                percent_died_round, "percent_died_round"
            )

            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            if args.verbose:
                print_banner(
                    "COVID19 Report({}):: deaths: {}, confirmed: {}, recovered: {}, percent_died: {}".format(
                        dt_string, deaths, confirmed, recovered, percent_died_round
                    )
                )

            print()
            print(
                colored("({}) Covid19! Report:::  ".format(dt_string), "cyan"), end=""
            )
            print(
                colored(
                    "Confirmed({})({}): {},".format(
                        confirmed_symbol, confirmed_diff, confirmed
                    ),
                    "blue",
                ),
                end="",
            )
            print(
                colored(
                    " Recovered({})({}): {},".format(
                        recovered_symbol, recovered_diff, recovered
                    ),
                    "green",
                ),
                end="",
            )
            print(
                colored(
                    " Deaths({})({}): {},".format(deaths_symbol, deaths_diff, deaths),
                    "red",
                ),
                end="",
            )
            print(
                colored(
                    " Percentage Died({})({}): {}".format(
                        percent_died_round_symbol,
                        percent_died_round_diff,
                        percent_died_round,
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
        time.sleep(3600)


if __name__ == "__main__":
    main()
