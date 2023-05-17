import os, re
import requests  # pip install requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        # Kiedy pojawia się błąd, funkcja otwiera stronę apology.html i przekazuje jej komunikat.
        # Generator memów, użyty na tej stronie, oczekuje komunikatów w formie GET, czyli w URL.
        # URL nie obsługuje wszystkich znaków. Twórca generatora wmyślił obejście, zastępowanie
        # jendych znaków innymi. Poniżej je implementujemy.
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    # Login_required to taka funkcja strażnik, napisana przez twórców Flaska.
    # 1. Przyjmuje oryginalną funkcję jako f.
    # 2. Definiuje nową funkcję, która zawiera starą + dodatkowy kod sprawdzający czy jest ciastko.
    # 3. Zwraca nową funkcję. Ta, jeśli ciastko istnieje, zwróci funkcję oryginalną.

    # Czyli login_required to automat pakujący - przyjmuje funkcję f i zwraca decorated_function.
    # Decorated_function to paczka zawierająca nasz oryginał f z dodatkowym kodem.
    # Kod sprawdzi czy jest ciastko. Jeśli tak, decorated_function zwróci oryginalną funkcję f.

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Połącz się z API:
    try:
        api_key = os.environ.get("API_KEY")

        # Stwórz URL z nazwą firmy i kluczem API:
        # ...quote_plus() - bierze symbol oznaczający firmę i konwertuje go do postaci bezpiecznej dla URL;
        # np. '/El Niño/' -> '%2FEl+Ni%C3%B1o%2F'
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"

        # zapisz odpowiedź serwera w zmiennej response:
        response = requests.get(url)

        # jeśli pojawi się błąd podczas pobierania obiektu z URL, zwróć obiekt HTTPError który wyjaśni, co się stało:
        response.raise_for_status()

    except requests.RequestException:
        return None

    # Przetwórz odpowiedź na zmienne:
    try:
        # Zamień odpowiedź serwera na obiekt JSON o nazwie quote,
        # wyciągnij z niego 3 wartości i zwróć z naszymi krótszymi nazwami: name, price i symbol:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"],
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


# Wyciaganie numeru użytkownika z ciastka.
# id=session["user_id"] nie dało się go zadeklarować raz, na górze programu w app.py, bo występował błąd.
# Musiało być deklarowane we wnętrzu funkcji związanej z HTTP.
# Nie dało się go zadeklarować raz, wewnątrz login albo index, bo nie wychodziło poza scope.
# Było deklarowane w wielu funkcjach od nowa. Wrzucenie go do funkcji w helpers skróciło i uprościo kod.
def id():
    return session["user_id"]


def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    # Sprawdzenia re.search zwracają dopasowany obiekt lub None. Dopisanie do nich 'is None' zwraca Boolean:
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None

    # overall result
    password_ok = not (
        length_error
        or digit_error
        or uppercase_error
        or lowercase_error
        or symbol_error
    )

    return {
        "password_ok": password_ok,
        "length_error": length_error,
        "digit_error": digit_error,
        "uppercase_error": uppercase_error,
        "lowercase_error": lowercase_error,
        "symbol_error": symbol_error,
    }
