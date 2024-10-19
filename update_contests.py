import json
import requests
import os  # Import os module to access environment variables

# Function to determine the division based on contest name
def get_division(contest_name):
    name_lower = contest_name.lower()
    if "educational" in name_lower:
        return "ED2"
    if "div. 1 + div. 2" in name_lower:
        return "D1+2"
    if "div. 1" in name_lower:
        return "D1"
    if "div. 2" in name_lower:
        return "D2"
    if "div. 3" in name_lower:
        return "D3"
    if "div. 4" in name_lower:
        return "D4"
    return "Unknown"

# Function to extract contest ID from href property
def extract_contest_id(href):
    return href.split('/')[-1]  # Extracts the last part of the URL (the contest ID)

# Load existing data from the JSON file
with open('filtered_data.json', 'r') as file:
    existing_data = json.load(file)

# Retrieve the API key from environment variables
api_key = os.getenv("CLIST_API_KEY")
if not api_key:
    raise ValueError("API key not found in environment variables")

# API call
api_url = f"https://clist.by/api/v4/contest/?username=RahulHarpal&api_key={api_key}&limit=3000&total_count=true&with_problems=false&upcoming=false&format_time=false&resource=codeforces.com&start__gte=2024-09-21T08%3A10%3A00&order_by=start"
response = requests.get(api_url).json()

# Compare API response with existing data
new_contests = response.get("objects", [])
for contest in new_contests:
    contest_id = extract_contest_id(contest["href"])  # Use href to get the contest ID
    if contest_id not in existing_data:
        division = get_division(contest["event"])
        existing_data[contest_id] = {
            "pCount": contest.get("n_statistics", 0),  # pCount is n_statistics
            "name": contest["event"],
            "div": division,  # Use the division determined by the function
            "startTime": contest["start"]
        }

# Save updated data back to the JSON file
with open('filtered_data.json', 'w') as file:
    json.dump(existing_data, file, indent=4)

print(f"{len(new_contests)} contests checked, new contests added.")
