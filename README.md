# mx-elections-2021-bridge

Bridge to connect Google Spreadsheets with the [mx-elections-2021](https://github.com/Socialtic/mx-elections-2021) API.

## Runing scripts

### Pipeline

Read data, process it and populate an empty database 

* `python pipeline.py <local|fb>`
	
### Updater

Compare data from GSheet and previously saved (`dataset/person_old.csv`) and
update changes, additions and deletions on the API. 

* `python updater.py`

## Dependencies

* Install dependencies with:

```
$ pip install -r requirements.txt
```

* `python >= 3.6`

## Architecture

This pipeline have strong dependency with Google Spreadsheets where information,
previously retrieve from multiple source by a team, is placed. There are two sheets:

### Capture Sheet

Information about candidates. We consider the next fields:

|||||
| --------- |-----------|--------------|-----------|	
| person_id | role_type | first_name   | last_name |
| full_name | nickname  | abbreviation | coalition |
| state     | area      | membership_type | start_date
| end_date  | is_substitute | is_titular |date_birth
| gender    | dead_or_alive | last_degree_of_studies | profession_[1-6]
| Website   | URL_FB_page |URL_FB_profile | URL_IG
| URL_TW    | URL_others | URL_photo | source_of_truth 

### Struct Sheet

Static tables and catalogs

* Area
* Chamber
* Role
* Coalition
* Party
* Contest
* Profession
* Url types

With this information we can **populate an empty database** using `pipeline.py`
module or **update** existing data using `updater.py` module. Also, the module
`check_predictions.py` compare Facebook Url predictions with capture sheet and
save the differences into `predictions/`.

## Modules

### 0. `sheets.py` and `auth.py`

First we need a method to connect `python` with the spreadsheets. With this
modules we manage spreadsheets manipulation and authentication respectively

**NOTE**: You need a Developer Google account to get an api token
(like `credential.json` file) for `auth.py` script.

#### Relevant links

* [Sheet API Docs](https://developers.google.com/sheets/api).
* [Get started as a Workspace developer](https://developers.google.com/workspace/guides/getstarted-overview).

### 1. `static_tables.py`

This module read and store in memory static tables. This tables will be send
to the API and also be required to build dynamic tables.

### 2. `pipeline.py`

This module reads the capture and static sheets and make three operations:

1. Runs a few
[validations](https://github.com/Socialtic/mx-elections-2021-bridge/blob/main/validations.py)
(`validations.py`). The founded errors are saved into `errors/`. The tested
fields are the follow:
	* last_name
	* membership_type
	* dates
	* urls
	* professions
2. Build dynamic tables
	* Using static tables and catalogs
3. Upload static and dynamic data to the API
	* Additionally, the module saves a `csv` copy of database into `csv_db/`.

**NOTE**: This module require an empty database from the API since it reads all
information from capture sheet and sned it.

### 3. `updater.py` (WIP)

This module compare current capture data (`dataset/person_current.csv`) with
previous data (`dataset/person_old.csv`). The difference are sent to the API
and logged into `logs/` in three different types:

1. Changes
2. Additions
3. Deletions

**NOTE**: Due to the time constraints of the project this module has a status
of Work in Progress (WIP).

#### TODO Feature

* [ ] Replace automatically person_old.csv with person_current.csv information
  once the data update is complete.
* [ ] Test the script

## Data examples

An example of how capture sheets looks like can be found at `data_samples/` 
