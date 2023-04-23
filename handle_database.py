import pymysql
import json

with open("mysql_config.json", "r") as mysql_config:
    config = json.load(mysql_config)

HOST = config["host"]
USER = config["user"]
PASSWORD = config["password"]

# create dictionary to store the sql CREATE TABLE commands
TABLES = dict()
TABLES["cities"] = """
            CREATE TABLE IF NOT EXISTS cities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                top_attractions_url VARCHAR(255)
            );"""

TABLES["attractions"] = """
            CREATE TABLE IF NOT EXISTS attractions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                city_id INT,
                url VARCHAR(255),
                FOREIGN KEY (city_id) REFERENCES cities(id)
            );"""

TABLES["attraction_stats"] = """
            CREATE TABLE IF NOT EXISTS attraction_stats (
                attraction_id INT,
                ranking INT,
                num_reviewers INT,
                excellent_review INT,
                very_good_review INT,
                average_review INT,
                poor_review INT,
                terrible_review INT,
                FOREIGN KEY (attraction_id) REFERENCES attractions(id)
            );"""

TABLES["popular_mentions"] = """
            CREATE TABLE IF NOT EXISTS popular_mentions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                popular_mention VARCHAR(255)
            );"""

TABLES["popular_mentions_attractions"] = """
            CREATE TABLE IF NOT EXISTS popular_mentions_attractions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                attraction_id INT,
                popular_mention_id INT,
                FOREIGN KEY (attraction_id) REFERENCES attractions(id),
                FOREIGN KEY (popular_mention_id) REFERENCES popular_mentions(id)
            );"""

TABLES["meteorological_data"] = """
            CREATE TABLE IF NOT EXISTS attraction_stats (
                min_temp INT,
                max_temp INT,
                mean_temp INT,
                total_precipitation INT,
                FOREIGN KEY (city_id) REFERENCES cities(id)
            );"""
#
# TABLES["demography"] = """
#             CREATE TABLE IF NOT EXISTS attraction_stats (
#                 Var_1 INT,
#                 Var_2 INT,
#                 Var_3 INT,
#                 Var_4 INT,
#                 Var_5 INT,
#                 FOREIGN KEY (city_id) REFERENCES cities(id)
#             );"""

# create dictionary to store the sql INSERT INTO commands
INSERT_INTO = dict()
INSERT_INTO["cities"] = (
    " INSERT INTO cities (name) "
    " VALUES (%s);"
)

INSERT_INTO["attractions"] = (
    " INSERT INTO attractions (name, city_id, url) "
    " VALUES (%s, (SELECT id FROM cities WHERE cities.name=%s), %s);"
)

INSERT_INTO["attraction_stats"] = (
    " INSERT INTO attraction_stats "
    "(attraction_id, ranking, num_reviewers, excellent_review, very_good_review, "
    " average_review, poor_review, terrible_review) "
    "VALUES ((SELECT id FROM attractions WHERE attractions.name=%s), %s, %s, %s, %s, %s, %s, %s) "
)

INSERT_INTO["popular_mentions"] = (
    " INSERT INTO popular_mentions (popular_mention) "
    " VALUES (%s) "
)

INSERT_INTO["popular_mentions_attractions"] = (
    " INSERT INTO popular_mentions_attractions (attraction_id, popular_mention_id) "
    " VALUES ("
    "   (SELECT id FROM attractions WHERE name=%s),"
    "   (SELECT id FROM popular_mentions WHERE popular_mention=%s)"
    ") "
)

INSERT_INTO["meteorological_data"] = (
    " INSERT INTO meteorological_data "
    "(city_id, min_temp, max_temp, mean_temp, total_precipitation) "
    "VALUES ((SELECT name FROM cities WHERE name=%s), %s, %s, %s, %s) "
)


# INSERT_INTO["demography"] = (
#             " INSERT INTO demography "
#             "(city_id, Var_1, Var_2, Var_3, Var_4, Var_5) "
#             "VALUES ((SELECT name FROM cities demography name=%s), %s, %s, %s, %s, %s, %s, %s) "
#         )


def already_recorded(var, data_table):
    """
    param: var (str) - a variable name
    param: var (data_table) - a data_table name in DB
    return: (boolean) - Return True if the variable is already in the chosen data_table of the Attractions database
    """
    with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM {} WHERE name="{}";'.format(data_table, var))
        existing_records = c.fetchall()
        if existing_records is None or len(existing_records) == 0:
            return False
        else:
            return True


# def city_already_recorded(city):
#     """
#     param: city (str) - a city name
#     return: (boolean) - Return True if the city is already in the cities table of the Attractions database
#     """
#     with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
#         c = conn.cursor()
#         c.execute('SELECT * FROM cities WHERE name="{}";'.format(city))
#         existing_records = c.fetchall()
#         if existing_records is None or len(existing_records) == 0:
#             return False
#         else:
#             return True
#
#
# def attraction_already_recorded(attraction):
#     """
#     param: attraction (str) - An attraction name
#     return: (boolean) - return True if the attraction is already in the attractions table of the Attractions database
#     """
#     with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
#         c = conn.cursor()
#         c.execute('SELECT * FROM attractions WHERE name="{}";'.format(attraction))
#         existing_records = c.fetchall()
#         if existing_records is None or len(existing_records) == 0:
#             return False
#         else:
#             return True
#
#
# def popular_mention_already_recorded(popular_mention):
#     """
#     param: popular_mention (str) a "popular_mention"
#     return: (boolean) - Return True if the popular_mention has already been recorded in the popular_mention table.
#     """
#     with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
#         c = conn.cursor()
#         c.execute('SELECT * FROM popular_mentions WHERE popular_mention="{}"'.format(popular_mention))
#         existing_records = c.fetchall()
#         if existing_records is None or len(existing_records) == 0:
#             return False
#         else:
#             return True
#

def meteorological_data(met_df):
    """
    params: (Pandas.DataFrame) - the data which was created using an external script.
    The structure of the dataframe is as follows (generated using pd.DataFrame.columns)
    'Name', 'min_temp', 'max_temp', 'mean_temp', 'total_precipitation'
    return: no return, function insert the data in to the attraction Data Base

    """
    with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
        c = conn.cursor()
        for index, city in met_df.iterrows():
            if already_recorded(city["Name"], "meteorological_data"):
                continue  # move to the next attraction

            if not already_recorded(city["Name"], "meteorological_data"):
                c.execute(INSERT_INTO["meteorological_data"], (city["Name"], city["min_temp"],
                                                               city["max_temp"], city["mean_temp"],
                                                               city["total_precipitation"]))
                conn.commit()
    return


def populate_tables(attraction_df):
    """
    params: (Pandas.DataFrame) - the data which was created using an external script.
        The structure of the dataframe is as follows (generated using pd.DataFrame.columns)
        'City', 'Name', 'Popular Mentions', 'Score',
           'Reviewers#', 'Excellent', 'Very good', 'Average', 'Poor', 'Terrible',
           'Excellent_ratio', 'VG_ratio', 'Average_ratio', 'Poor_ratio', 'Terrible_ratio', 'Url'
    return: no return, function insert the data in to the attraction Data Base
    """
    with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
        c = conn.cursor()
        for index, attraction in attraction_df.iterrows():
            if already_recorded(attraction["Name"], "attractions"):
                continue  # move to the next attraction

            if not already_recorded(attraction["City"], "cities"):
                c.execute(INSERT_INTO["cities"], (attraction["City"],))

            c.execute(INSERT_INTO["attractions"], (attraction["Name"], attraction["City"], attraction["Url"]))
            c.execute(INSERT_INTO["attraction_stats"], (attraction["Name"], attraction["Tripadvisor rank"],
                                                        attraction["Reviewers#"], attraction["Excellent"],
                                                        attraction["Very good"], attraction["Average"],
                                                        attraction["Poor"], attraction["Terrible"]))
            conn.commit()

            for popular_mention in attraction["Popular Mentions"]:  # only add the record if it isn't there already
                if already_recorded(popular_mention, "popular_mentions"):
                    c.execute(INSERT_INTO["popular_mentions_attractions"], (attraction["Name"], popular_mention))
                    conn.commit()
                else:  # popular mention not yet recorded
                    c.execute(INSERT_INTO["popular_mentions"], (popular_mention,))
                    c.execute(INSERT_INTO["popular_mentions_attractions"], (attraction["Name"], popular_mention))
                    conn.commit()
    return


def create_database():
    """
    This function is used to create the Attractions database, whose design can be found
    on the gitHub repo of this project: https://github.com/yoniabrams/webscraper_tripadvisor
    """
    with pymysql.connect(host=HOST, user=USER, password=PASSWORD) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE database IF NOT EXISTS Attractions;")

    with pymysql.connect(host=HOST, user=USER, password=PASSWORD, database="Attractions") as conn:
        cursor = conn.cursor()
        # create all the tables (if each table doesn't exist already, respectively)
        for sql_table_creation_script in TABLES.values():
            cursor.execute(sql_table_creation_script)
