import os, re
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters

        When an error occurs, the function opens the apology.html page and gives it a GET message.
        Characters that cannot be implemented in the URL are replaced by others.
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

    Decorative function. Takes the original function as f.
    Defines a new function (decorated_function) that contains the old one + code to check if there is a cake.
    If the cake exists it will return the original function. If not, it will redirect to the login page.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Connect to API:
    try:
        api_key = os.environ.get("IEX_API_KEY")

        # Create URLs with company name and API key.
        # ...quote_plus() - takes the symbol denoting the company and converts it
        # to a URL-safe form; i.e. '/El Niño/' -> '%2FEl+Ni%C3%B1o%2F'
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"

        # Store the server's response in the 'response' variable:
        response = requests.get(url)

        # if an error occurs while retrieving an object from a URL,
        # return an HTTPError object that explains what happened:
        response.raise_for_status()

    except requests.RequestException:
        return None

    # Process the response to the variables:
    try:
        # Turn the server response into a JSON object named 'quote',
        # extract 3 values from it and return with shorter names: name, price and symbol:
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


def id():
    # Extracting a user number from a cookie.

    # id = session["user_id"] could not be declared once, at the top of the program in app.py,
    # because there was an error. It had to be declared inside an HTTP-related function.

    # It could not be declared once, inside login or index, because it would not go outside the scope.
    # It was declared in many functions from scratch. Putting it into functions in helpers shortened and simplified the code.
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

    # searching for digits.
    # The 're.search' checks return a matched object or None. Adding 'is None' to them returns a Boolean:
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
