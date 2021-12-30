# P13 Nurse Agenda

## About

This project aims to provide an agenda that serves as a timeline.

The principle is to be able to share it between partners who have events in common when they take turns working.

The basis of the project is to provide this shared schedule and it would then be possible to integrate operating data of a practice, such as turnover progress and other things.

## Installation

1. Clone the repo

```sh
git clone https://github.com/Jerome-LorD/p13_nurse_agenda.git
```

2. Create and activate a virtual environment

```py
python -m venv env
```

```sh
linux: source env/bin/activate
windows: env/Scripts/activate
```

3. With `psql`, create the database and a user

```sql
CREATE DATABASE <yourDb> OWNER <yourUser>;
```

4. Install the requirements.txt

```sh
pip install -r requirements.txt
```

5. Create a `.env` file at the root of the project.

```py
DB_ORIGIN_BASE_NAME=<yourDbName>
DB_ORIGIN_BASE_PASSWD=<yourPassword>
DB_APP_USER=<yourUserName>
HOST=<yourHOST>
```
