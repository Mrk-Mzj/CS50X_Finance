# Functions supporting the database

from cs50 import SQL

db = SQL("sqlite:///finance.db")


def cash_of(id):
    # Checking how much cash the user has.
    # The base is written so that for "cash" it will not return an empty object.
    # User in database always has some cash.
    # Hence, I immediately write [0]["cash"], without risk of error.

    return db.execute("SELECT cash FROM users WHERE id=?", id)[0]["cash"]


def check_username(id):
    # Checking the username assigned to id

    return db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]


def delete_sum_up(id, of_company):
    # Removal of all shares, if the user sells the whole thing

    db.execute(
        "DELETE FROM ownership WHERE person_id=? AND of_company=?",
        id,
        of_company,
    )


def read_history(id):
    # Loading the user's transaction history

    return db.execute(
        "SELECT when_did, did_what, how_many, for_price, of_company FROM purchases WHERE person_id=? ORDER BY when_did ASC",
        id,
    )


def password_update(hash, id):
    db.execute("UPDATE users SET hash=? WHERE id=?", hash, id)


def possessions_of(id):
    # Checking what and how many shares user has. This data will be displayyed
    # in the first two columns on the website.

    return db.execute(
        "SELECT how_many, of_company FROM ownership WHERE person_id=?", id
    )


def read_sum_up(id, of_company):
    # Checking how many shares the user has

    return db.execute(
        "SELECT how_many FROM ownership WHERE person_id=? AND of_company=?",
        id,
        of_company,
    )


def rows_of_id(id):
    # Loading login data by id

    return db.execute("SELECT * FROM users WHERE id = ?", id)


def rows_of_username(username):
    # Loading login data by username

    return db.execute("SELECT * FROM users WHERE username = ?", username)


def save_balance(balance, id):
    # Saving the current amount in the user's account (the 'users' table)

    db.execute("UPDATE users SET cash=? WHERE id=?", balance, id)


def save_purchase(id, did_what, shares, for_price, of_company):
    # Recording of operations in the detailed list of transactions (table 'purchases')

    db.execute(
        "INSERT INTO purchases (when_did, person_id, did_what, how_many, for_price, of_company) VALUES (datetime('now'), ?, ?, ?, ?, ?)",
        id,
        did_what,
        shares,
        for_price,
        of_company,
    )


def save_sum_up(id, sum_up, of_company):
    # Record the number of shares if the user has had zero so far

    db.execute(
        "INSERT INTO ownership (person_id, how_many, of_company) VALUES (?,?,?)",
        id,
        sum_up,
        of_company,
    )


def save_user(username, hash):
    # Adding a new user to the database
    db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)


def update_sum_up(id, sum_up, of_company):
    # Update the number of shares a user has had so far

    db.execute(
        "UPDATE ownership SET how_many=? WHERE person_id=? AND of_company=?",
        sum_up,
        id,
        of_company,
    )
