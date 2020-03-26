import os
from utils import load_credentials


API_KEY, API_SECRET = load_credentials()


if __name__ == "__main__":
    print("API_KEY", API_KEY)
    print("API_SECRET", API_SECRET)
