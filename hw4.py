"""
Creating a pandas DataFrame from a csv file. Also some practice using SQL on a class database.
"""

import pandas as pd
import numpy as np


def csv_to_dataframe(csv_filename):
    """
    Takes a CSV file name and converts the contents into a pandas DataFrame.

    :param csv_filename: csv file to convert.
    :return: a DataFrame object of the csv file contents.
    """

    return pd.read_csv(csv_filename, decimal=',', index_col="Country")


def format_df(df):
    """
    Formats the DataFrame so that it's indicies are stripped of white space and all data in the Region column
    is converted to titlecase and stripped.

    :param df: DataFrame to format.
    :return: None
    """
    indices = []
    for i in df.index:
        indices.append(i.strip)
        df.loc[i, "Region"] = df.loc[i, "Region"].title().strip()

    df.rename(str.strip, axis="index", inplace=True)
    return None


def growth_rate(df):
    """
    Adds a "Growth Rate" column to the DataFrame by subtracting the Deathrate from the Birthrate.

    :param df: DataFrame to add on to
    :return: None
    """

    growth_rates = []
    for i in df.index:
        birth_rate = df.loc[i, "Birthrate"]
        death_rate = df.loc[i, "Deathrate"]

        growth_rates.append(birth_rate - death_rate)

    df["Growth Rate"] = growth_rates
    return None


def dod(p, r):
    """
    This function takes an initial population and a growth rate (which must be negative – why?) in 1000's of individuals
    per year and returns the number of years it will take for the population of the country to go extinct if the growth
    rate doesn't change. We consider the population extinct if it is down to no more than two individuals, but this
    stretches out the time considerably because of the way the math of exponential decay works. 1,000 or 10,000
    individuals would probably be more reasonable definition of extinct.

    :param p: population
    :param r: growth rate
    :return: number of years it will take for the population of the country to go extinct
    """
    num_yrs = 0
    while p > 2:
        p = p + p * r / 1000
        num_yrs += 1
    return num_yrs


def years_to_extinction(df):
    """
    This function takes a formatted countries DataFrame that has a Growth Rate column and adds a column labeled
    'Years to Extinction'. Initialize the values in this column to np.nan: Replace the NaN in the new column for every
    country that has a negative growth rate with the number of years until the population is extinct:

    :param df:
    :return:
    """
    df["Years to Extinction"] = np.nan

    for i in df.index:
        gr = df.loc[i, "Growth Rate"]
        if gr > 0 or pd.isna(gr):
            continue

        df.loc[i, "Years to Extinction"] = dod(df.loc[i, "Population"], df.loc[i, "Growth Rate"])
    return None


def dying_countries(df):
    """
    Creates a Series with all the countries and their years until they're dead.

    :param df: a formatted DataFrame
    :return:
    """
    data = []
    for i in df.index:
        if df.loc[i, "Growth Rate"] < 0:
            data.append([df.loc[i, "Years to Extinction"], i])

    data = sorted(data)
    ser = {}
    for i in range(len(data)):
        ser[data[i][1]] = data[i][0]

    s = pd.Series(ser)
    return s


def class_performance(conn, table_name="ISTA_131_F17"):
    """
    Creates a dictionary that maps the grades to their 1-decimanl point precision percentages of the class that got
    that grade.

    :param conn: a connection object to a database
    :param table_name: name of the table to work with.
    :return: dictionary with grades mapped to percentages of students with the grade.
    """

    c = conn.cursor()
    query = "SELECT grade, COUNT(*) FROM " + table_name + " GROUP BY grade"
    grades = c.execute(query).fetchall()

    total = 0
    for i in grades:
        total += i[1]

    summary = {}
    for grade in grades:
        summary[grade[0]] = round((grade[1] / total) * 100.0, 1)

    return summary


def improved(conn, table1, table2):
    """
    Finds the students who received better grades in the class represented by the second table name than in the
    first table name.

    :param conn: a connection to a database
    :param table1: first table name
    :param table2: second table name
    :return: list of students last names who did better in the second class (table)
    """
    c = conn.cursor()
    query = "SELECT " + table1 + ".last FROM " + table1 + " LEFT OUTER JOIN " + table2 + " ON " + table1 + ".last = " \
            + table2 + ".last WHERE " + table1 + ".grade < " + table2 + ".grade ORDER BY " + table1 + ".last ASC;"
    students = c.execute(query).fetchall()

    last_names = []
    for s in students:
        last_names.append(s[0])
    return last_names


def main():
    """
    Main creates a frame from countries_of_the_world.csv, formats the frame, adds Growth Rate and Years to Extinction
    columns to it, and prints the top 5 dying countries.
    """

    countries_df = csv_to_dataframe("countries_of_the_world.csv")
    format_df(countries_df)
    growth_rate(countries_df)
    years_to_extinction(countries_df)

    dying = dying_countries(countries_df)

    i = 0
    for country, val in dying.items():
        if i >= 5:
            break
        print(country + ": " + str(val) + " Years to Extinction")
        i += 1


if __name__ == '__main__':
    main()
