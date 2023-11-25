# CS50 Finance

import os
from cs50 import SQL

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *
from db import *


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
# usd is a function in helpers.py which makes currency formatting easier
app.jinja_env.filters["usd"] = usd

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Make sure API key is set
if not os.environ.get("IEX_API_KEY"):
    raise RuntimeError("IEX_API_KEY environment variable not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    # Cache is turned off so changes that we make were always updated by the browser
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Login_required to funkcja dekorująca, stworzona w helpers.py.
# Redirects non-loggers to the login page.
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

    if request.method == "POST":
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # data check:

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

        # Check if your new password is secure:

        elif password_check(password)["password_ok"] == False:
            return apology("must be: 8 long, 1 digit, 1 symbol, 1 upper, 1 lower", 403)
        # password_check("a") returns:
        # {'password_ok': False, 'length_error': True, 'digit_error': True, 'uppercase_error': True, 'lowercase_error': False, 'symbol_error': True}

        # Check if the old password matches:

        # loading login data
        rows = rows_of_id(id())

        # Make sure the user exists and the old_password entered matches the database
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], old_password):  # type: ignore
            # type: ignore is an info for Pylance snot to highlight an error in the code from the CS50 authors.
            # Pylance is worried that asking for a password might return None and blow up the code. Unnecessarily.
            # If you managed to load the data about the user: len(rows)=1, then among them will be the password.
            return apology("invalid old password", 403)

        # hash the password
        hash = generate_password_hash(password)

        # update the password on the current user
        password_update(hash, id())

        # redirect to login:
        return redirect("/login")

    else:
        return render_template("change_password.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    grand_total = 0

    # Preparation of data for table 1:

    possessions = possessions_of(id())

    # Next, we check how much a share of each company currently costs (current_price)
    # and how much money the user has from them as a result (total_value).
    # I add this data to the previous ones. They land in the 3rd and 4th column of the table on www.

    for possession in possessions:
        # querying the API for the dataset for the currently checked company
        current = lookup(possession["of_company"])

        # if the API returns a response, we complete the current_price of this company
        if current:
            possession["current_price"] = usd(current["price"])

            # and we calculate how much they are worth to the user
            possession["total_value"] = usd(current["price"] * possession["how_many"])

            # we also begin to calculate the sum of his total assets
            grand_total = grand_total + (current["price"] * possession["how_many"])

    # Preparation of data for table 2:

    # Checking how much cash the user has
    cash = cash_of(id())

    # Sending all data for display
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

    # if the user specified the symbol of the company he is looking for:
    if request.method == "POST":
        # check that the symbol is given
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide company symbol", 403)

        # check if there is a company for this symbol
        lookups = lookup(symbol)
        if lookups == None:
            return apology("there is no such company", 403)

        # check if 'shares' exists and is > 0
        # note: forms in Flask always return STR by default
        shares = request.form.get("shares", type=int)
        if not shares or shares <= 0:
            return apology("please provide positive INT value", 403)

        # Checking how much cash the user has
        cash = cash_of(id())

        # see if he can afford to buy
        if cash < (lookups["price"] * shares):
            return apology("not enough cash", 403)

        # Save the transaction in the detailed list of transactions (table 'purchases')
        for_price = lookups["price"]
        of_company = lookups["symbol"]
        save_purchase(id(), "bought", shares, for_price, of_company)

        # Save the reduced amount in the user's account (table 'users')
        balance = cash - (shares * for_price)
        save_balance(balance, id())

        # Update the list of share holders (table 'ownership')

        # 1 - get the number of shares of a given company that the user has:
        sum_up = read_sum_up(id(), of_company)

        # 2 - update the number of shares:
        # a) if user buys shares of this company for the first time
        if not sum_up:
            sum_up = shares
            save_sum_up(id(), sum_up, of_company)

        # b) if user buys shares of this company once again
        else:
            sum_up = sum_up[0]["how_many"] + shares
            update_sum_up(id(), sum_up, of_company)

        return redirect("/")

    # if he entered via GET:
    else:
        # ask username of company symbol:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    return render_template("history.html", history=read_history(id()))


# Login converts the entered password into a hash. Compares it with the hash in the database.
# Creates a cookie with the user id. This way paths know which user is logged in.
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

        # Loading login credentials by 'username'
        rows = rows_of_username(username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):  # type: ignore
            # The above note is info to Pylance not to highlight the error in the code from the authors.
            # Pylance points out that asking for a password may return None.
            # If you managed to load the user data: len(rows)=1, the password will be among them.
            return apology("invalid username and/or password", 403)

        # Remember which user id has logged in
        # I also add the name of the user so that the page can show the name of the person logged in.
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

    # if the user specified the symbol of the company he is looking for:
    if request.method == "POST":
        # check if the symbol is given
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide company symbol", 403)

        # checking if there is a company for this symbol
        lookups = lookup(symbol)
        if lookups == None:
            return apology("there is no such company", 403)

        # if the company exists pass the info about it to quoted.html
        return render_template("quoted.html", lookups=lookups)

    # if the user entered via GET:
    else:
        # ask username of company symbol:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # data check:

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
        # password_check("a") returns:
        # {'password_ok': False, 'length_error': True, 'digit_error': True, 'uppercase_error': True, 'lowercase_error': False, 'symbol_error': True}

        # At the very end I give the database reading.
        # Load information about a potential user with this login.
        # If successful, report that the login is already taken:
        rows = rows_of_username(username)
        if rows and (username == rows[0]["username"]):
            return apology("name already taken", 403)

        # hash the password
        hash = generate_password_hash(password)

        # add user to the database
        save_user(username, hash)

        # redirect to login page:
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # if the user specified the symbol of the company he is looking for:
    if request.method == "POST":
        # check if symbol is given
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide company symbol", 403)

        # check if there is a company for this symbol
        lookups = lookup(symbol)
        if lookups == None:
            return apology("there is no such company", 403)

        # check if 'shares' exists and is > 0
        # note: forms in Flask always return STR by default
        shares = request.form.get("shares", type=int)
        if not shares or shares <= 0:
            return apology("please provide positive INT value", 403)

        # Check how many shares the user has and how many he can sell:

        # check the number of shares of a particular company that the user has:
        of_company = lookups["symbol"]
        sum_up = read_sum_up(id(), of_company)

        # if user has these actions, clean up variable; if not, report error:
        if sum_up:
            sum_up = sum_up[0]["how_many"]
        else:
            return apology("you don't have shares of this company", 403)

        # see if the user can sell that much
        if sum_up < shares:
            return apology("you don't have this many shares", 403)

        # Save the transaction in the detailed list of transactions (table 'purchases')
        for_price = lookups["price"]
        save_purchase(id(), "sold", shares, for_price, of_company)

        # Checking how much cash the user has
        cash = cash_of(id())

        # Save the increased amount in the user's account (table 'users')
        balance = cash + (shares * for_price)
        save_balance(balance, id())

        # Update the list of share holders (table 'ownership')
        # a) if user sells all: delete row from database
        if shares == sum_up:
            delete_sum_up(id(), of_company)

        # b) if user sells part: update row in database
        else:
            sum_up -= shares
            update_sum_up(id(), sum_up, of_company)

        return redirect("/")

    # if he entered via GET:
    else:
        # ask username of company symbol:
        return render_template("sell.html")
