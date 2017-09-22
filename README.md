# Kibble Scanner Application
The Kibble Scanners collect information for the Kibble Suite.

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

 - Apache Pony Mail (`plugins/scanners/ponymail.py`)
 - Atlassian JIRA (`plugins/scanners/jira.py`)
 - BugZilla Issue Tracker (`plugins/scanners/bugzilla.py`)
 - Git Repository fetcher (`plugins/scanners/git-sync.py`)
 - GitHub issues/PRs (`plugins/scanners/github.py`)
 - GNU Mailman Pipermail (`plugins/scanners/pipermail.py`)
 


