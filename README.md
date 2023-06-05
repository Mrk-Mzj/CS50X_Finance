# 🪙 Harvard's CS50X Flask project: Finance

See how well you would do on the real stock market. 

Start with a certain amount of virtual money. Buy and sell shares of NASDAQ-listed companies at real-time prices. See if you would make money by playing the real stock market.

🪧Note: This is final project for CS50: Introduction to Computer Science 2022. Boilerplate code was provided with the list of functionalities that needed to be implemented.


# 1. Installation

### 1.1 Obtaining an API key for IEX Cloud:
To gain access to current stock quotes.

1. Go to IEX Cloud and register by clicking 'Start a Free Trial' button:
https://iexcloud.io/cloud-login#/register
It will give you a seven-day trial period.

2. Select API Tokens and copy publishable token:

![Alt text](_screenshots/IEX%20-%20msedge_Yb5sudcCfA.jpg)

3. Set environment variable:

```bash
bash:
export IEX_API_KEY="pk_..."
```

``` PowerShell 
PowerShell:
set IEX_API_KEY="pk_..."
```
You can check if it is set correctly by typing: 
```
echo $IEX_API_KEY
```

### 1.2 Installing Flask:
For front and backend integration.
```
pip install Flask
```

### 1.3 Installing Flask-Session:
Support for server-side sessions.
```
pip install Flask-Session
```

### 1.4 Installing CS50:
For simplified SQL operation.
```
pip install cs50
```

### 1.5 Installing Requests:
For HTTP/1.1 requests handling.
```
pip install requests
```

# 2. Usage

Run flask:
``` bash
flask --debug run
```

Flask will give you a link to the website. Open it in your browser:
```
Running on http://127.0.0.1:5000
```
You'll see a welcome screen, when you can register or log in:

![Alt text](_screenshots/Register%20-%20msedge_0aMRTRvlbN.jpg)
![Alt text](_screenshots/Login%20-%20msedge_dMIj8vofpU.jpg)

### After logging in you will see your home screen with stocks and cash balance:

![Alt text](_screenshots/Home%20screen%20-%20Wallet%20-%20msedge_kVBPxVnUZB.jpg)

### You can chceck current prices:

![Alt text](_screenshots/Quote%20-%20msedge_eER9Lb5yab.jpg)
![Alt text](_screenshots/Quote%202%20-%20msedge_tX1YTtommr.jpg)

### Buy, Sell and check your account history:

![Alt text](_screenshots/Buy%20-%20msedge_sPGIKGEEds.jpg)
![Alt text](_screenshots/Sell%20-%20msedge_kflhtlk4kU.jpg)
![Alt text](_screenshots/History%20-%20msedge_4gLtmB4vZ7.jpg)

### You can also change your password at the right hand side:

![Alt text](_screenshots/Change%20password%20-%20msedge_dxr5g7xktf.jpg)
...or log out completly.

# 3. Contributing
This is a learning project. There is no need to develop it any further.

# 4. License
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
Boilerplate code by Harvard's CS50 Creators.
