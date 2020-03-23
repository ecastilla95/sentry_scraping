# sentry_scraping

This program works only if you have the required permission to manage Security in HUE.

This program exports all the Apache Sentry permissions / permits / roles into a TSV file.

It uses a web browser and web scrapping techniques, so make sure you have Firefox installed and that you have entered HUE through firefox at least once.

There are two files:
 - sentry.sh: installs the gecko driver for Linux and Mozilla Firefox
 - sentry.py: exports the metadata to the output.
