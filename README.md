# The Select Four

For this database project, we created The Select Four database to reflect updates and changes made to the baseball
database provided in CSI 3335.

## Authors

- Salma Battisha
- Misty Kurien
- Priscilla Leafblad
- Ciara Woodahl

## Installation

Use our setup sql file to load the database.

```bash
\. SQLSetup_selectfour.sql

MariaDB [selectfour]> show databases;

CREATE DATABASE selectfour;

use selectfour;

\. selectfour.sql
```

All our files work within the provided virtual environment.
The csi3335F23.py file includes the setup for the running database.

This is the pip freeze for reference:

```bash
alembic==1.12.0
blinker==1.6.2
click==8.1.7
colorama==0.4.6
scikit-learn==1.3.2
scipy==1.11.4
six==1.16.0
SQLAlchemy==2.0.21
threadpoolctl==3.2.0
typing_extensions==4.8.0
tzdata==2023.3
Werkzeug==2.3.7
WTForms==3.0.1

```

## Webpage Features

- User registration
- User login and logout
- User account with editable bio
- User's last seen time is stored and accessible by admin
- Secure access to search pages; must be logged in to view pages
- All teams are linked to their respective information for the year displayed
- Admin registration with required security key "123"
- Admin view logs functionality showing all executed queries for each user
- Pythagorean projections of team wins shown
- Divisions and division standings shown
- Manager details are shown
- Managers who are also players have both their manager and player information shown

## Database Changes

- 2022 data loaded onto the database
- 2023 awards data added
- Cleaned data from CSVs and rearranged columns to match structure of our database
- Eliminated duplicate records and ensured no loss of data
- Lost data in the updated Lahman database restored in Batting, Parks, People, PitchingPost, and Schools
- ID names changed for normalization purposes and to ensure that JOINs work seamlessly
