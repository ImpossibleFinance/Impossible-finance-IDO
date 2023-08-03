# Impossible-finance-IDO

The dashboard provides investors with a seamless and transparent IDO process. It allows investors to view all the available IDOs and their details, including the start and end dates of the IDO, the amount being raised, the price of the token, and the allocation limits. Investors can also participate in the IDO through the dashboard by connecting their wallets to the platform.

All the libraries that were used are in the ***requirements.txt*** file 

## Links: 🥳

- Public Link: https://ido.impossible.finance/


## Usage on localhost

### Setup ⛏️

1. Create `.env` file
2. Put your BSCscan and Arbiscan API key there like `API_KEY_BNB = "..."` or `API_KEY_ARB = "..."`
3. Make a `csv_data` repository

### Run 🤖

Run via python and get all data as CSV file:
```basg
Upload_app.py
```

Or you can set up crontab -e script and get data every minute/hour/day

Start the UI:
```basg
gunicorn app:server -b:8080
```

### Some snapshots 📸

![image](https://github.com/0xKARTOD/Impossible-finance-IDO/assets/100310858/d6e28d8e-dfd8-450f-a611-3afb12218466)
