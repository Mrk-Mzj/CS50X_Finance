# API_KEY zapisałem w pliku tekstowym. Ustawiamy go w bash:
# export API_KEY=pk_3b6cf277dec74af49ff62d8c0f2e22d4
#
# (dla CMD komenda set API_KEY)
# i ew. restartujemy konsolę.
# Dla bash i powershell komendy brzmią trochę inaczej.
# Zmienne można też wpisać na stałe, w ustawieniach systemu.
# flask --debug run

# Marek hasło: a, Czarek: b, Darek: c, Jarek: qweQWE123!@#, Lech: qwaQWA123!@#

# TODO: ew. napisz testy jednostkowe
# TODO: ew. możesz zmienić cs50 na natywną bibliotekę SQL Pythona lub na SQLAlchemy


import os
from cs50 import SQL

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, id, password_check
from db import (
    cash_of,
    check_username,
    delete_sum_up,
    read_history,
    password_update,
    possessions_of,
    read_sum_up,
    rows_of_id,
    rows_of_username,
    save_balance,
    save_purchase,
    save_sum_up,
    save_user,
    update_sum_up,
)


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# usd to funkcja w helpers.py; ułatwia formatowanie walut.
app.jinja_env.filters["usd"] = usd

# Konfiguruj aplikację by ciastka sesji były trzymane w lokalnym systemie, np. na dysku.
# Tak, jak robiliśmy to już wcześniej. Flask na domyślnych ustawieniach tworzyłby sesje
# w cyfrowo podpisanych ciastkach.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    # Wyłączamy cache by zmiany, jakie robimy w plikach, były zawsze widziane przez przeglądarkę
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Login_required to funkcja dekorująca, stworzona w helpers.py.
# Przekierowuje niezalogowanych do strony logowania.
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

    if request.method == "POST":

        old_password = request.form.get("old_password")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # sprawdzenie danych:

        if not old_password:
            return apology("must provide old password", 403)

        elif not password:
            return apology("must provide password", 403)

        elif not confirmation:
            return apology("must confirm password", 403)

        elif password != confirmation:
            return apology("must provide two identical passwords", 403)

        elif password == old_password:
            return apology("must provide password different than previous one", 403)

        # Sprawdź czy nowe hasło jest bezpieczne:

        elif password_check(password)["password_ok"] == False:
            return apology("must be: 8 long, 1 digit, 1 symbol, 1 upper, 1 lower", 403)
        # password_check("a") zwraca:
        # {'password_ok': False, 'length_error': True, 'digit_error': True, 'uppercase_error': True, 'lowercase_error': False, 'symbol_error': True}

        # Sprawdź czy stare hasło się zgadza:

        # wczytanie danych logowania
        rows = rows_of_id(id())

        # upewnij się, że user istnieje i wpisane old_password zgadza się z bazą danych
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], old_password):  # type: ignore
            # Powyższy dopisek to info do Pylance by nie podkreślał błędu w kodzie od autorów.
            # Pylance martwi się, że pytanie o hasło może zwrócić None i wywalić kod. Niepotrzebnie.
            # Jeśli udało się wczytać dane o userze: len(rows)=1, to wśród nich będzie hasło.
            return apology("invalid old password", 403)

        # haszuj hasło
        hash = generate_password_hash(password)

        # aktualizuj hasło u bieżącego użytkownika
        password_update(hash, id())

        # przekieruj do logowania:
        return redirect("/login")

    else:
        return render_template("change_password.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    grand_total = 0

    # Przygotowanie danych do tabeli 1:

    possessions = possessions_of(id())

    # Następnie sprawdzamy, ile obecnie kosztuje akcja każdej ze spółek (current_price)
    # i ile w związku z tym user ma z nich pieniędzy (total_value).
    # Te dane dopisuję do poprzednich. Wylądują w 3 i 4 kolumnie tabeli na www.

    for possession in possessions:

        # odpytujemy API o zestaw danych dla aktualnie sprawdzanej spółki
        current = lookup(possession["of_company"])

        # jeśli API zwróci odpowiedź, uzupełniamy current_price tej spółki
        if current:
            possession["current_price"] = usd(current["price"])

            # i obliczamy ile są warte dla usera
            possession["total_value"] = usd(current["price"] * possession["how_many"])

            # zaczynamy też obliczać sumę jego całego majątku
            grand_total = grand_total + (current["price"] * possession["how_many"])

    # Przygotowanie danych do tabeli 2:

    # Sprawdzenie, ile gotówki ma user
    cash = cash_of(id())

    # Wysłanie wszystkich danych do wyświetlenia
    return render_template(
        "index.html",
        possessions=possessions,
        cash=usd(cash),
        grand_total=usd(grand_total + cash),
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # jeśli user podał symbol szukanej spółki:
    if request.method == "POST":

        # sprawdź czy podano symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide company symbol", 403)

        # sprawdź czy istnieje spółka dla tego symbolu
        lookups = lookup(symbol)
        if lookups == None:
            return apology("there is no such company", 403)

        # sprawdź czy shares istnieje i jest > 0
        # uwaga: formularze we Flask domyślnie zawsze zwracają STR
        shares = request.form.get("shares", type=int)
        if not shares or shares <= 0:
            return apology("please provide positive INT value", 403)

        # Sprawdzenie, ile gotówki ma user
        cash = cash_of(id())

        # sprawdź czy stać go na zakup
        if cash < (lookups["price"] * shares):
            return apology("not enough cash", 403)

        # Zapisz transakcję w szczegółowym wykazie transakcji (tabl. purchases)
        for_price = lookups["price"]
        of_company = lookups["symbol"]
        save_purchase(id(), "bought", shares, for_price, of_company)

        # Zapisz pomniejszoną kwotę na koncie usera (tabl. users)
        balance = cash - (shares * for_price)
        save_balance(balance, id())

        # Zaktualizuj wykaz posiadaczy akcji (tabl. ownership)

        # 1 - pobierz ilość akcji danej spółki, które ma user:
        sum_up = read_sum_up(id(), of_company)

        # 2 - zaktualizuj ilość akcji:
        # a) jeśli user kupuje akcje tej spółki po raz pierwszy
        if not sum_up:
            sum_up = shares
            save_sum_up(id(), sum_up, of_company)

        # b) jeśli user kupuje akcje tej spółki po raz kolejny
        else:
            sum_up = sum_up[0]["how_many"] + shares
            update_sum_up(id(), sum_up, of_company)

        return redirect("/")

    # jeśli wszedł przez GET:
    else:
        # zapytaj usera o symbol spółki:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    return render_template("history.html", history=read_history(id()))


# Login zamienia wprowadzone hasło na hasz. Porównuje go z haszem w bazie danych.
# Tworzy ciastko z id użytkownika. W ten sposób ścieżki wiedzą, który user jest zalogowany.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Wczytanie danych logowania po username
        rows = rows_of_username(username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):  # type: ignore
            # Powyższy dopisek to info do Pylance by nie podkreślał błędu w kodzie od autorów.
            # Pylance martwi się, że pytanie o hasło może zwrócić None i wywalić kod. Niepotrzebnie.
            # Jeśli udało się wczytać dane o userze: len(rows)=1, to wśród nich będzie hasło.
            return apology("invalid username and/or password", 403)

        # Remember which user id has logged in
        # Dodaję też imię usera, żeby stronka mogła pokazać imię zalogowanej osoby
        session["user_id"] = rows[0]["id"]
        session["user_name"] = check_username(id())

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """look up a stock’s current price."""

    # jeśli user podał symbol szukanej spółki:
    if request.method == "POST":

        # sprawdzenie czy podano symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide company symbol", 403)

        # sprawdzenie czy istnieje spółka dla tego symbolu
        lookups = lookup(symbol)
        if lookups == None:
            return apology("there is no such company", 403)

        # jeśli istnieje przekaż info o niej do quoted.html
        return render_template("quoted.html", lookups=lookups)

    # jeśli wszedł przez GET:
    else:
        # zapytaj usera o symbol spółki:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # sprawdzenie danych:

        if not username:
            return apology("must provide username", 403)

        if not username.isalnum():
            return apology("user name alphanumerical only", 403)

        elif not password:
            return apology("must provide password", 403)

        elif not confirmation:
            return apology("must confirm password", 403)

        elif password != confirmation:
            return apology("must provide two identical passwords", 403)

        elif password_check(password)["password_ok"] == False:
            return apology("must be: 8 long, 1 digit, 1 symbol, 1 upper, 1 lower", 403)
        # password_check("a") zwraca:
        # {'password_ok': False, 'length_error': True, 'digit_error': True, 'uppercase_error': True, 'lowercase_error': False, 'symbol_error': True}

        # Na samym końcu daję czytanie bazy danych.
        # Załaduj informacje o potencjalnym użytkowniku z tym loginem.
        # Jeśli się uda, zgłoś, że login jest już zajęty:
        rows = rows_of_username(username)
        if rows and (username == rows[0]["username"]):
            return apology("name already taken", 403)

        # haszuj hasło
        hash = generate_password_hash(password)

        # dodaj usera do bazy danych:
        save_user(username, hash)

        # przekieruj do logowania:
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # jeśli user podał symbol szukanej spółki:
    if request.method == "POST":

        # sprawdź czy podano symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide company symbol", 403)

        # sprawdź czy istnieje spółka dla tego symbolu
        lookups = lookup(symbol)
        if lookups == None:
            return apology("there is no such company", 403)

        # sprawdź czy shares istnieje i jest > 0
        # uwaga: formularze we Flask domyślnie zawsze zwracają STR
        shares = request.form.get("shares", type=int)
        if not shares or shares <= 0:
            return apology("please provide positive INT value", 403)

        # Sprawdź, ile udziałów ma user i ile może sprzedać:

        # sprawdź ilość akcji danej spółki, które ma user:
        of_company = lookups["symbol"]
        sum_up = read_sum_up(id(), of_company)

        # jeśli user ma te akcje, oczyść zmienną; jeśli nie, zgłoś błąd:
        if sum_up:
            sum_up = sum_up[0]["how_many"]
        else:
            return apology("you don't have shares of this company", 403)

        # sprawdź czy user może tyle sprzedać
        if sum_up < shares:
            return apology("you don't have this many shares", 403)

        # Zapisz transakcję w szczegółowym wykazie transakcji (tabl. purchases)
        for_price = lookups["price"]
        save_purchase(id(), "sold", shares, for_price, of_company)

        # Sprawdzenie, ile gotówki ma user
        cash = cash_of(id())

        # Zapisz powiększoną kwotę na koncie usera (tabl. users)
        balance = cash + (shares * for_price)
        save_balance(balance, id())

        # Zaktualizuj wykaz posiadaczy akcji (tabl. ownership)
        # a) jeśli user sprzedaje wszystkie: usuń wiersz z bazy
        if shares == sum_up:
            delete_sum_up(id(), of_company)

        # b) jeśli user sprzedaje część: zaktualizuj wiersz w bazie
        else:
            sum_up -= shares
            update_sum_up(id(), sum_up, of_company)

        return redirect("/")

    # jeśli wszedł przez GET:
    else:
        # zapytaj usera o symbol spółki:
        return render_template("sell.html")
