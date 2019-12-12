# YNAB -You Need a Budget

Budgeting Tool helps you plan and manage your personal budget.
In Ynab you have budgets, each budget has one or more accounts with transactions.

## Run tests

    python -m pytest

### Developer API

* https://api.youneedabudget.com/    
    
    
#User API
 
     ynab-import --s swedbank -r api -w api
     ynab-import --s swedbank -r file.csv -w file.csv
     ynab-import --s swedbank -r file.csv -w api
 
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
