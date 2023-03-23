# Records by Lambda
### Finance record keeping app

This app uses a remote MySql server to store finance data, and can perform operations such as delete, update/add, fetch and download data from/to the database, as the case may be.

# What can it do?

1. To avoid session only saving, I have connected the web app to a remote database (MySQL).
2. User can write to and fetch from the remote database.
3. Fetching can be done by either using "All" to fetch all entries or using a custom number input to fetch particular number of rows .
4. User can delete "a number" of last few entries from the database, in case of wrong entries. I have this button hidden in an expander to avoid "Click mistake".
5. Fetched data returns a dataframe from the database, and can be "downloaded" as a CSV file.
