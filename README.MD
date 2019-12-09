# YNAB -You Need a Budget

Budgeting Tool helps you plan and manage your personal budget.
In Ynab you have budgets, each budget has one or more accounts with transactions.

## Run tests

    python -m pytest

### Developer API

* https://api.youneedabudget.com/



# CSVPRovider - Reads from csv file
    * SwedBankCSVProvider
    * RevolutCSVProvider
    # idea if possible: Takes input metadata how to read from csv and output dataclass (set default and allow override)
# APIProvider
    * SwedBankAPIProvider
    * RevolutAPIProvider
    # Takes nessesory arguments for initialization and  output dataclass (set default and allow override)
# Transformation
    * Generic class
    * Needs From Dataclass to Dataclass
    * Needs spesific transformation logics
    * Should be possible to use on list of data
# Runner
    *  Based on configuration loads and runs providers and transformations
    
    
    
#User API


User spesifies 
 which bank are you importinh [swedbank, revolut]
 where to get transaction data [read_from_csv_file, read_from_api]
 import mode [output_import_csv, import_using_API]
 
 
 ynab-import --source swedbank --read-from api --write-to api
 ynab-import --source swedbank --read-from file --write-to file
 ynab-import --source swedbank --read-from file --write-to api
 
 Some default/extra configurations required
 
 * read-from file
    * INPUT_FILE_PATH [default (~/{bank}.csv) home@Linux] (actual full file path required)
 * read-from api
    * appropriate bank credentials and setup required
    * Raise Not Supported
 * write to file 
    * OUTPUT_FILE_PATH [default (~/{bank}-ynab-{date-time}.csv) home@Linux] (add file name only if not specified)
 * write to api 
    * YNAB_API_KEY
    * YNAB_BUDGET_ID

YNAB_API_BASE_URL="https://api.youneedabudget.com/v1/"



#### User Wiki


##### Ynab 

####### Import Manually

Its posisble to import Csv File manually


####### Import Using Ynab API
To set up this integration you need to create `Personal Access Token`.

Go to `https://app.youneedabudget.com/settings/developer` and click `New Token` 
