#!/usr/local/bin/python3
"""Grab some info about covid19."""

import argparse
import json
import os
import sys
from argparse import RawDescriptionHelpFormatter

import pandas as pd
import requests


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
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as req:
        req.raise_for_status()
        with open(local_filename, 'wb') as file:
            for chunk in req.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    file.write(chunk)
                    # f.flush()
    return local_filename


class Covid19:
    """Process all inputs from the user."""

    def __init__(self, args):
        """Initialize all variables from argparse if any."""
        self.force = args.force
        self.verbose = args.verbose

    def get_rest(self, url):
        """Get the REST API and process the results."""
        response = requests.request("GET", url)
        response.raise_for_status() # raise exception if invalid response
        if self.verbose:
            json_object = json.loads(response.text)
            json_formatted_str = json.dumps(json_object, indent=2)
            print(json_formatted_str)
        return response.json()

    def display_user_inputs(self):
        """Display all user inputs in a pretty way."""
        if not self.verbose:
            return

        print_banner(
            "Force = {}, Verbose = {}".format(
                self.force,
                self.verbose,
            )
        )

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

    try:
        covid19 = Covid19(args)
        covid19.display_user_inputs()
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
        deaths = int(covid19.get_csv_crunch_total(url))
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
        confirmed = int(covid19.get_csv_crunch_total(url))
        url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
        recovered = int(covid19.get_csv_crunch_total(url))
        percent_died = (deaths / confirmed * 100)

        print_banner('COVID19 Report:: deaths: {}, confirmed: {}, recovered: {}, percent_died: {}'.format(deaths, confirmed, recovered, str(round(percent_died, 2))))
    except Exception:
        print("Exception caught:")
        print(sys.exc_info())
        raise


if __name__ == "__main__":
    main()
