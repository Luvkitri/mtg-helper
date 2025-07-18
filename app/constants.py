import os

from dotenv import load_dotenv

# Get envs
load_dotenv()

# SQLITE
CWD = os.getcwd()
SQLITE_ = os.environ.get("SQLITE_DATABASE")

# CONSTS
MAX_LIMIT = 50
MAX_OFFSET = 100
