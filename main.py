import sys

if __name__ != "__main__":
    print("This is the main file. Do not call.")
    sys.exit()

import requests

from get_input_class import GetInput

# Creates class for receiving user input
user_input = GetInput() # Declares class, initializes date variables, obtains Pixela API configs
user_input.get_pixela_data() # Obtains data from Pixela for the current date
user_input.get_input_type() # Asks the user what they want to do. Allows for changing date here.
user_input.get_val() # Gets number of hours or minutes to change from user

# If the user enters an updated value of 0, this is ignored and the program ends.
if user_input.new_val == 0:
    print("\nNo update pushed. Press Enter to exit.")
    input()
    sys.exit()

# json data to send to Pixela
update_json = {
    "date": user_input.date_to_update,
    # Adds together the current value on Pixela to the new value provided by the user
    "quantity": "0" + str(user_input.existing_val + user_input.new_val),
    "thanksCode": user_input.THANKS_CODE,
}

# Posts the update to Pixela
update_graph = requests.post(url = f"{user_input.PIXELA_ENDPOINT}/{user_input.USERNAME}/graphs/{user_input.graph_id}", headers = user_input.headers, json = update_json)

# Informs user of the results. Should be 200, but any errors will list here.
print(f"\nSent {user_input.date_to_user} update, with {round(user_input.new_val, 2)} hours/{round(user_input.new_val * 60, 2)} minutes.")
print(f"\n{update_graph}")
print(update_graph.text)

# Shows user the new value for the relevant date (or displays error)
try:
    print(f"\n{user_input.date_to_user} value:\n" + requests.get(url =f"{user_input.PIXELA_ENDPOINT}/{user_input.USERNAME}/graphs/{user_input.graph_id}/{user_input.date_to_update}", headers = user_input.headers).text)
except Exception as json_load_e:
    print(f"Error loading json data:\n{json_load_e}")

input("\nPress enter to exit.\n")