import cowsay
import sys

# instalujemy pakiet Cowsay (zewnętrzny folder z modułami) poleceniem: "pip install cowsay". Więcej ciekawych pakietów na PyPI.org
# uruchamiamy z konsoli: python "kurs CS50 - 06 - modules 02 - PACKAGES.py"

# jeśli program zostaje uruchomiony z dopisanym dokładnie 1 parametrem
if len (sys.argv) == 2:

    # uruchom funkcję cow z pakietu cowsay
    cowsay.cow("Hello " + sys.argv[1])