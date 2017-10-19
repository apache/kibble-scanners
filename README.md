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
 - Gerrit Code Review (`plugins/scanners/gerrit.py`)
 - Git Repository Fetcher (`plugins/scanners/git-sync.py`)
 - Git Census Counter (`plugins/scanners/git-census.py`)
 - Git Code Evolution Counter (`plugins/scanners/git-evolution.py`)
 - Git SLoC Counter (`plugins/scanners/git-sloc.py`)
 - GitHub Issues/PRs (`plugins/scanners/github.py`)
 - GitHub Traffic Statistics (`plugins/scanners/github-stats.py`)
 - GNU Mailman Pipermail (`plugins/scanners/pipermail.py`)
 

## Requirements:

 - [cloc](https://github.com/AlDanial/cloc) version 1.70 or later
 - git binaries
 - python3 (3.3 or later)
 - python3-elasticsearch 
 - python3-dateutils
 
# Get involved
  TBD. Please see https://kibble.apache.org/ for details!
  