# Imports
from dydx3.constants import API_HOST_SEPOLIA, API_HOST_MAINNET
from decouple import config

#!!!! Select MODE DEV vs PROD !!!!
MODE = "DEVELOPEMENT"

############################ MAIN Execusion Sequence ############################
# 1- Close all open positions and orders
ABORT_ALL_POSITIONS = True

# 2- Find Cointegrated Pairs
FIND_COINTEGRATED = False

# 3- Manage Exits
MANAGE_EXITS = False

# 4- Place Trades
PLACE_TRADES = False

############################ MAIN Execusion Sequence ############################

# Resolution
RESOLUTION = "1HOUR"
# Stats Window
WINDOW = 21
# API import limit
LIMIT = 100

# Thresholds - Opening and closing ---------------------
# static param for the mean reverse pair trading, 24 default
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 1.5 
# the amount of to be used for each trade
USD_PER_TRADE = 100
# the max amount we want the bot to trade
USD_MIN_COLLATERAL = 10000

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True
# ------------------------------------------------


# KEYS for Connection --------------------------
#DEV Wallet Private KEY METAMASK /!\FIRST TO GET FUNDS /!\ AND SECOND IS FOR SENDING FUNDS
ETHEREUM_ADDRESS = "0x5f583893c53F420d3D1DBe079BF73d04C4dbCa70"
# DEV KEYS DYDX
STARK_PRIVATE_KEY_TESTNET = config("STARK_PRIVATE_KEY_TESTNET")
DYDX_API_KEY_TESTNET = config("DYDX_API_KEY_TESTNET")
DYDX_API_SECRET_TESTNET = config("DYDX_API_SECRET_TESTNET")
DYDX_API_PASSPHRASE_TESTNET = config("DYDX_API_PASSPHRASE_TESTNET")

# PROD KEYS DYDX
# STARK_PRIVATE_KEY_MAINNET = config("STARK_PRIVATE_KEY_MAINNET")
# DYDX_API_KEY_MAINNET = config("DYDX_API_KEY_MAINNET")
# DYDX_API_SECRET_MAINNET = config("DYDX_API_SECRET_MAINNET")
# DYDX_API_PASSPHRASE_MAINNET = config("DYDX_API_PASSPHRASE_MAINNET")

# KEYS Export 
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_TESTNET if MODE == "DEVELOPEMENT" else "STARK_PRIVATE_KEY_MAINNET"
DYDX_API_KEY = DYDX_API_KEY_TESTNET if MODE == "DEVELOPEMENT" else "DYDX_API_KEY_MAINNET"
DYDX_API_SECRET = DYDX_API_SECRET_TESTNET if MODE == "DEVELOPEMENT" else "DYDX_API_SECRET_MAINNET"
DYDX_API_PASSPHRASE = DYDX_API_PASSPHRASE_TESTNET if MODE == "DEVELOPEMENT" else "DYDX_API_PASSPHRASE_MAINNET"

# HOST Export
HOST = API_HOST_SEPOLIA if MODE == "DEVELOPEMENT" else API_HOST_MAINNET
HTTP_PROVIDER = "https://eth-sepolia.g.alchemy.com/v2/SxmonSk4JSyLJgukmD6pXcdFHoWA51Gy" if MODE =="DEVELOPEMENT" else ""