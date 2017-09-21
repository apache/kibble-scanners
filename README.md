# Kibble Scanner Application
The Kibble Scanners collect information for the Apache Kibble Suite.

## Setup instructions:

 - Edit conf/config.yaml to match your Kibble service

## How to run:

 - On a daily/weekly/whatever basis, run: `python3 src/kibble-scanner.py`.
 
## Directory structure:

 - `conf/`: Config files
 - `src/`:
 - - `kibble-scanner.py`: Main script for launching scans
 - - `plugins/`:
 - - - `brokers`: The various database brokers (ES or JSON API)
 - - - `utils`: Utility libraries
 - - - `scanners`: The individual scanner applications

## Currently available scanner plugins:

 - Apache Pony Mail
 - Atlassian JIRA
 - BugZilla Issue Tracker
 - GitHub issues/PRs
 - GNU Mailman Pipermail
 


