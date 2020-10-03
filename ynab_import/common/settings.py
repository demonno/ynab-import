from environs import Env

env = Env()
env.read_env()

INPUT_FILE_PATH = None
OUTPUT_FILE_PATH = None

SOURCE = env.str("SOURCE")
READ_FROM = env.str("READ_FROM")
WRITE_TO = env.str("WRITE_TO")

# Ynab Config
YNAB_API_BASE_URL = "https://api.youneedabudget.com/v1/"
YNAB_API_KEY = env.str("YNAB_API_KEY")
YNAB_BUDGET_ID = env.str("YNAB_BUDGET_ID")
YNAB_ACCOUNT_ID = env.str("YNAB_ACCOUNT_ID")
