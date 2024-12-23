import json
import requests
import time
import os
import subprocess

# API endpoint
API_URL = "https://codeforces.com/api/blogEntry.comments?blogEntryId=137639"
JSON_FILE = "handles.json"

# Load existing data from JSON file
def load_handles_data():
    try:
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save data to JSON file
def save_handles_data(handles_data):
    with open(JSON_FILE, "w") as file:
        json.dump(handles_data, file, indent=4)

# Function to add new tourist handles efficiently
def add_tourist_handles(comments, handles_data):
    tourist_handles = handles_data.get("Tourist", ["tourist"])  # Initialize with existing or default
    tourist_set = set(tourist_handles)  # Use a set for efficient lookups

    for comment in comments:
        text = comment.get("text", "").lower()
        commentator_handle = comment.get("commentatorHandle", "")

        if "tourist" in text and commentator_handle not in tourist_set:
            tourist_handles.append(commentator_handle)
            tourist_set.add(commentator_handle)

    handles_data["Tourist"] = tourist_handles
    return handles_data

# Function to commit changes to the repository
def commit_changes():
    try:
        # Configure Git identity (if not already set globally)
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)

        # Fetch remote changes to avoid push conflicts
        subprocess.run(["git", "pull", "--rebase"], check=True)

        # Stage, commit, and push changes
        subprocess.run(["git", "add", JSON_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Update handles data"], check=True)
        subprocess.run(
            ["git", "push", f"https://{os.getenv('GITHUB_PAT')}@github.com/rahulharpal1603/json.git", "HEAD:main"],
            check=True,
        )
        print("Changes committed and pushed to repository.")
    except subprocess.CalledProcessError as e:
        print(f"Error while committing changes: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Main script to poll the API every 5 minutes for 1 hour
def main():
    handles_data = load_handles_data()  # Load existing data
    start_time = time.time()

    while time.time() - start_time < 3600:  # Run for 1 hour
        try:
            response = requests.get(API_URL)
            response.raise_for_status()

            data = response.json()
            if data["status"] == "OK":
                comments = data["result"]
                handles_data = add_tourist_handles(comments, handles_data)

                # Save updated data to the JSON file
                save_handles_data(handles_data)
                print(f"Updated handles.json with {len(handles_data['Tourist'])} handles.")

                # Commit the changes every 5 minutes
                commit_changes()

        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Error occurred: {e}")

        time.sleep(300)  # Wait for 5 minutes before polling again

if __name__ == "__main__":
    main()
