import sys

if __name__ == "__main__":
    print("This is a supporting file. Do not execute this directly.")
    sys.exit()

import datetime
import requests
import json
import os

from logins import PIXELA_ENDPOINT, USERNAME, graph_id, TOKEN, THANKS_CODE
from logo import logo

class GetInput:
    def __init__(self):
        self.date_vars() # Sets up variables for dates
        self.PIXELA_ENDPOINT = PIXELA_ENDPOINT
        self.USERNAME = USERNAME
        self.graph_id = graph_id
        self.TOKEN = TOKEN
        self.THANKS_CODE = THANKS_CODE # Only actually used in main.py
        self.headers = {"X-USER-TOKEN": self.TOKEN} # Sets up header for API request

    # This configures needed variables for dates. Called upon class initialization and called when user wants to change to a custom date.
    def date_vars(self, new_date = None):
        # self.date_obj is the date under consideration. Datetime object. Defaults to today's date, but if new_date is passed in, then uses that instead.
        if new_date == None: self.date_obj = datetime.datetime.now()
        else: self.date_obj = new_date

        self.date_to_user = self.date_obj.strftime('%B %#d, %Y') # Formatted to show to user
        self.date_to_update = self.date_obj.strftime("%Y%m%d") # Formatted to be compatible with Pixela

    def print_date_info(self): # displays date overview information
        print(logo)
        print(f"Current value for {self.date_to_user}: {round(self.existing_val, 2)} hours/{round(self.existing_val * 60)} minutes.")

    def clear_screen(self): os.system("cls")

    def get_pixela_data(self):
        print("\nCommunicating with Pixela API...")
        # Make a date request. This should never throw an error; the worst case scenario is a 404 or other unexpected response.
        self.date_request = requests.get(url=f"{self.PIXELA_ENDPOINT}/{self.USERNAME}/graphs/{self.graph_id}/{self.date_to_update}", headers=self.headers)
        self.clear_screen()

        # Obtaining the relevant day's value. If the day has nothing assigned (0 hours), Pixela will return a 404 error.
        self.existing_val = 0
        if self.date_request.status_code == 200:  # Date in question has existing data
            # Obtains relevant day's data, received as a JSON file, converts to dict, extracts quantity (hours), converts from str to float.
            self.existing_val = float(json.loads(self.date_request.text)["quantity"])
            # self.existing_val = float(json.loads(requests.get(url=f"{self.PIXELA_ENDPOINT}/{self.USERNAME}/graphs/{self.graph_id}/{self.date_to_update}",headers=self.headers).text)["quantity"])
            # Informs the user of the relevant day's current value (hours).
            self.print_date_info()
        elif self.date_request.status_code == 404:
            # If date's webpage does not exist, the user is informed that there is no data for this date. The user-supplied data here will be the first data for this date.
            print(logo)
            print(f"No data for {self.date_to_user}.")
        elif self.date_request.status_code == 500:
            print(logo)
            print(f"Pixela internal server error. Retry.\n\nStatus code:\n{self.date_request.status_code}\n\nResponse (text):\n{self.date_request.text}\n\nPress Enter to exit.\n")
            input()
            sys.exit()
        elif self.date_request.status_code == 503:
            print(logo)
            print(f"Pixela service unavailable. Site is likely down.\n\nStatus code:\n{self.date_request.status_code}\n\nResponse (text):\n{self.date_request.text}\n\nPress Enter to exit.\n")
            input()
            sys.exit()
        else:
            # Status code should ONLY be 200 (existing data) or 404 (no data yet but this process will add first data). Anything else requires investigation.
            print(logo)
            input(f"Unexpected status code response for {self.date_to_user}:\n{self.date_request.status_code}\n\nPress Enter to exit.\n")
            sys.exit()

    # Accepts user's input for changing current date's coding time (or changing the date)
    def get_input_type(self):
        self.input_accepted = False
        while self.input_accepted == False:
            self.hours_min = input("\n1. Hours\n2. Minutes\n3. Change date\n\n")
            if self.hours_min.strip().lower() == "exit" or self.hours_min.strip().lower() == "close": sys.exit()
            if self.hours_min not in ["1", "2", "3"]:
                print("\nPlease select 1, 2, or 3.")
                continue
            self.input_accepted = True # Input is accepted if it's 1, 2, or 3, but will be changed later if the user is changing the date below (so the user has a chance to specify hours or minutes after changing the date).

            # Defaults to hours unless the user has specified otherwise
            self.units = "hours"
            if self.hours_min == "2": self.units = "minutes"

            # For changing the date, self.input_accepted is set to False to run the loop again so the user can say if they're changing hours or minutes
            if self.hours_min == "3":
                self.get_new_date()
                self.input_accepted = False

    # Obatining the date the user wants to update if not the current date
    def get_new_date(self):
        self.date_valid = False
        while self.date_valid == False:
            # Date formats to be tested against. Add any formats to this tuple to improve user input options.
            date_parse_list = ("%m/%d/%y", "%m/%d/%Y", "%b %d %y", "%b %d %Y", "%B %d %y", "%B %d %Y")

            new_date = input("\nWhat date do you want to change?\n")
            # Strip input, change possible delimiters to "/", remove any commas (e.g., "August 1, 2022")
            new_date = new_date.strip().replace("-", "/").replace(".", "/").replace(",", "")

            if new_date.lower() == "exit" or new_date.lower() == "close": sys.exit()

            if new_date == "":
                print("\nPlease enter a date.")
                continue

            if new_date.lower() == "back":
                self.clear_screen()
                self.print_date_info()
                return

            # Loops through all date format options.
            # First loop attempt tests user's input with year appended as different strings (e.g., "/2022" and " 2022"). Second tries it assuming user provided the year.
            # If formatting succeeds, breaks out of the loop.
            cur_year = str(datetime.datetime.now().year)
            user_date_append = ("/" + cur_year, " " + cur_year)

            self.new_date_obj = None
            for parse_attempt in date_parse_list:
                if self.new_date_obj != None: break
                for date_append in user_date_append:
                    try: self.new_date_obj = datetime.datetime.strptime(new_date + date_append, parse_attempt)
                    except: self.new_date_obj = None
                    else: break

            if self.new_date_obj == None:
                for parse_attempt in date_parse_list:
                    try: self.new_date_obj = datetime.datetime.strptime(new_date, parse_attempt)
                    except: self.new_date_obj = None
                    else: break

            if self.new_date_obj == None: print("\nCould not parse. Please try again.\n") # Validation failed
            # Validation succeeded. Changes class date variables to new date, displays the new date's data to the user, and ends the while loop
            else:
                if self.new_date_obj.date() > datetime.datetime.today().date():
                    input("\nYou cannot enter data for a date in the future.\n\nPress Enter to return to the main menu.\n")
                    self.clear_screen()
                    self.print_date_info()
                    return
                self.date_vars(self.new_date_obj)
                self.get_pixela_data()
                self.date_valid = True

    # Finding out how many hours or minutes the user wants to change.
    def get_val(self):
        self.input_accepted = False
        while self.input_accepted == False:
            self.new_val = input(f"\nHow many additional {self.units} (as a float)?\n")
            if self.new_val.strip().lower() == "exit" or self.new_val.strip().lower() == "close": sys.exit()
            try: self.new_val = float(self.new_val)
            except ValueError: print("\nPlease enter a valid float.")
            else:
                # Pixela is set to only accept hours, so if minutes are entered by user, they're converted to hours.
                if self.units == "minutes": self.new_val = round(self.new_val / 60, 2)

                self.input_accepted = True