# Convert [swedbank](http://swedbank.ee) CSV to [YNAB](http://ynab.com) CSV Format  


* Take only following columns: `Date, Payee, Memo, OUTFLOW, INFLOW`
    * Debit goes to `Outflow`
    * Credit goes to `Inflow`
* Remove Rows Containing text: `closing balance, Turnover, Opening balance`

### Example CSV export from [swedbank](http://swedbank.ee)

* `swedbank.csv`


### Example converted output file

* `ynab.csv`


### RUN


    python swedbank_to_ynab.py