# Funkcje obsługujące bazę danych

from cs50 import SQL

db = SQL("sqlite:///finance.db")


def cash_of(id):
    # Sprawdzenie, ile gotówki ma user.
    # Baza jest napisana tak, że dla cash nie zwróci obiektu pustego,
    # user w bazie zawsze ma jakąś gotówkę. Stąd od razu robię uporządkowywanie
    # zmiennej cash przez dopisanie [0]["cash"], bez obawy o błąd.

    return db.execute("SELECT cash FROM users WHERE id=?", id)[0]["cash"]


def check_username(id):
    # Sprawdzenie nazwy użytkownika przypisanej do id

    return db.execute("SELECT username FROM users WHERE id = ?", id)[0]["username"]


def delete_sum_up(id, of_company):
    # Usunięcie wszystkich akcji, jeśi user sprzedaje całość

    db.execute(
        "DELETE FROM ownership WHERE person_id=? AND of_company=?",
        id,
        of_company,
    )


def read_history(id):
    # Wczytanie historii transakcji użytkownika

    return db.execute(
        "SELECT when_did, did_what, how_many, for_price, of_company FROM purchases WHERE person_id=? ORDER BY when_did ASC",
        id,
    )


def password_update(hash, id):
    db.execute("UPDATE users SET hash=? WHERE id=?", hash, id)


def possessions_of(id):
    # Sprawdzenie, jakie akcje ma user i ile.
    # Te dane wylądują w dwóch pierwszych kolumnach na stronie www.

    return db.execute(
        "SELECT how_many, of_company FROM ownership WHERE person_id=?", id
    )


def read_sum_up(id, of_company):
    # Sprawdzenie, ile akcji spółki ma user

    return db.execute(
        "SELECT how_many FROM ownership WHERE person_id=? AND of_company=?",
        id,
        of_company,
    )


def rows_of_id(id):
    # Wczytanie danych logowania po id

    return db.execute("SELECT * FROM users WHERE id = ?", id)


def rows_of_username(username):
    # Wczytanie danych logowania po username

    return db.execute("SELECT * FROM users WHERE username = ?", username)


def save_balance(balance, id):
    # Zapisanie aktualnej kwoty na koncie usera (tabl. users)

    db.execute("UPDATE users SET cash=? WHERE id=?", balance, id)


def save_purchase(id, did_what, shares, for_price, of_company):
    # Zapisanie operacji w szczegółowym wykazie transakcji (tabl. purchases)

    db.execute(
        "INSERT INTO purchases (when_did, person_id, did_what, how_many, for_price, of_company) VALUES (datetime('now'), ?, ?, ?, ?, ?)",
        id,
        did_what,
        shares,
        for_price,
        of_company,
    )


def save_sum_up(id, sum_up, of_company):
    # Zapisanie ilości akcji, jeśli user miał ich zero do tej pory

    db.execute(
        "INSERT INTO ownership (person_id, how_many, of_company) VALUES (?,?,?)",
        id,
        sum_up,
        of_company,
    )


def save_user(username, hash):
    # Dodanie nowego użytkownika do bazy danych
    db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)


def update_sum_up(id, sum_up, of_company):
    # Zaktualizowanie ilości akcji, które user miał do tej pory

    db.execute(
        "UPDATE ownership SET how_many=? WHERE person_id=? AND of_company=?",
        sum_up,
        id,
        of_company,
    )
