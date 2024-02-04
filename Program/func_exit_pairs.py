from constants import CLOSE_AT_ZSCORE_CROSS
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import place_market_order
import numpy as np
import json
import time

from pprint import pprint

# Manage trade exits
def manage_trade_exits(client):

  """
    Manage exiting open positions
    Based upon criteria set in constants
  """
  """
  The `manage_trade_exits` function is responsible for managing the exiting of open positions based on
  certain criteria set in the constants file.
  
  :param client: The `client` parameter is an object that represents the connection to the trading
  platform API. It is used to make API calls and interact with the trading platform
  :return: the string "complete" if there are no open positions or if there was an error in matching
  the open positions with the exchange records. Otherwise, it is returning the number of items
  remaining after closing positions and saving the file.
  """
  # Initialize saving output
  save_output = []

  # Opening JSON file
  try:
    open_positions_file = open("bot_agents.json")
    open_positions_dict = json.load(open_positions_file)
  except:
    return "complete"

  # Guard: Exit if no open positions in file
  # The code snippet `if len(open_positions_dict) < 1: return "complete"` is checking if there are no
  # open positions in the `open_positions_dict` dictionary. If there are no open positions, it
  # immediately returns the string "complete". This is used as a guard clause to exit the function early
  # if there are no open positions to manage.
  if len(open_positions_dict) < 1:
    return "complete"

  # Get all open positions per trading platform
  # The code snippet is retrieving all open positions from the trading platform API using the
  # `client.private.get_positions()` method. It specifies the status parameter as "OPEN" to only
  # retrieve open positions.
  exchange_pos = client.private.get_positions(status="OPEN")
  all_exc_pos = exchange_pos.data["positions"]
  markets_live = []
  # This code is used to create a list of all
  # the markets that have open positions in the trading platform.
  for p in all_exc_pos:
    markets_live.append(p["market"])

  # Protect API
  time.sleep(0.5)


  for position in open_positions_dict:

  # Check all saved positions match order record
  # Exit trade according to any exit trade rules
  # The code is iterating over each position in the `open_positions_dict` dictionary in the JESON file. For each
  # position, it extracts the matching information from the file for market 1 and market 2. It then
  # retrieves the order information for market 1 and market 2 from the trading platform API using the
  # `client.private.get_order_by_id()` method.
    
    # Initialize is_close trigger
    is_close = False

    # Extract position matching information from file - market 1
    position_market_m1 = position["market_1"]
    position_size_m1 = position["order_m1_size"]
    position_side_m1 = position["order_m1_side"]

    # Extract position matching information from file - market 2
    position_market_m2 = position["market_2"]
    position_size_m2 = position["order_m2_size"]
    position_side_m2 = position["order_m2_side"]

    # Protect API
    time.sleep(0.5)

    # Get order info m1 per exchange
    order_m1 = client.private.get_order_by_id(position["order_id_m1"])
    order_market_m1 = order_m1.data["order"]["market"]
    order_size_m1 = order_m1.data["order"]["size"]
    order_side_m1 = order_m1.data["order"]["side"]

    # Protect API
    time.sleep(0.5)

    # Get order info m2 per exchange
    order_m2 = client.private.get_order_by_id(position["order_id_m2"])
    order_market_m2 = order_m2.data["order"]["market"]
    order_size_m2 = order_m2.data["order"]["size"]
    order_side_m2 = order_m2.data["order"]["side"]

    # Perform matching checks
    # The code is checking if the market, size, and side
    # of the position in the JSON file match the market, size, and side of the order retrieved from
    # the trading platform API for market 1 and market 2.
    check_m1 = position_market_m1 == order_market_m1 and position_size_m1 == order_size_m1 and position_side_m1 == order_side_m1
    check_m2 = position_market_m2 == order_market_m2 and position_size_m2 == order_size_m2 and position_side_m2 == order_side_m2
    check_live = position_market_m1 in markets_live and position_market_m2 in markets_live

    # Guard: If not all match exit with error
    if not check_m1 or not check_m2 or not check_live:
      print(f"Warning: Not all open positions match exchange records for {position_market_m1} and {position_market_m2}")
      continue

    # Get prices
    series_1 = get_candles_recent(client, position_market_m1)
    time.sleep(0.2)
    series_2 = get_candles_recent(client, position_market_m2)
    time.sleep(0.2)

    # Get markets for reference of tick size
    markets = client.public.get_markets().data

    # Protect API
    time.sleep(0.2)

    # Trigger close based on Z-Score
    if CLOSE_AT_ZSCORE_CROSS:

      # Initialize z_scores
      # This code snippet calculates the current z-score for a spread between two series of data.
      hedge_ratio = position["hedge_ratio"]
      z_score_traded = position["z_score"]
      if len(series_1) > 0 and len(series_1) == len(series_2):
        spread = series_1 - (hedge_ratio * series_2)
        z_score_current = calculate_zscore(spread).values.tolist()[-1]

      # Determine Trade Close trigger /!\/!\/!\/!\/!\
      # The code snippet `z_score_level_check = abs(z_score_current) >= abs(z_score_traded)` is
      # checking if the absolute value of the current z-score is greater than or equal to the absolute
      # value of the traded z-score. This is used to determine if the z-score has reached a certain level
      z_score_level_check = abs(z_score_current) >= abs(z_score_traded)
      z_score_cross_check = (z_score_current < 0 and z_score_traded > 0) or (z_score_current > 0 and z_score_traded < 0)

      # Close trade
      if z_score_level_check and z_score_cross_check:
        # Initiate close trigger
        is_close = True

    ###
    # Add any other close logic you want here
    # Trigger is_close
    ###

    # Close positions if triggered 
    if is_close: # For test put 'not is_close' to make sure it will automatically close the positions 

      # Determine side - m1
      side_m1 = "SELL"
      if position_side_m1 == "SELL":
        side_m1 = "BUY"

      # Determine side - m2
      side_m2 = "SELL"
      if position_side_m2 == "SELL":
        side_m2 = "BUY"

      # Get and format Price
      price_m1 = np.float64(series_1[-1])
      price_m2 = np.float64(series_2[-1])
      accept_price_m1 = price_m1 * 1.05 if side_m1 == "BUY" else price_m1 * 0.95
      accept_price_m2 = price_m2 * 1.05 if side_m2 == "BUY" else price_m2 * 0.95
      tick_size_m1 = markets["markets"][position_market_m1]["tickSize"]
      tick_size_m2 = markets["markets"][position_market_m2]["tickSize"]
      accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
      accept_price_m2 = format_number(accept_price_m2, tick_size_m2)

      # Close positions
      try:

        # Close position for market 1
        print(">>> Closing market 1 <<<")
        print(f"Closing position for {position_market_m1}")

        close_order_m1 = place_market_order(
          client,
          market=position_market_m1,
          side=side_m1,
          size=position_size_m1,
          price=accept_price_m1,
          reduce_only=True,
        )

        print(close_order_m1["order"]["id"])
        print(">>> Closing <<<")

        # Protect API
        time.sleep(1)

        # Close position for market 2
        print(">>> Closing market 2 <<<")
        print(f"Closing position for {position_market_m2}")

        close_order_m2 = place_market_order(
          client,
          market=position_market_m2,
          side=side_m2,
          size=position_size_m2,
          price=accept_price_m2,
          reduce_only=True,
        )

        print(close_order_m2["order"]["id"])
        print(">>> Closing <<<")

      except Exception as e:
        print(f"Exit failed for {position_market_m1} with {position_market_m2}")
        save_output.append(position)

    # Keep record if items and save
    else:
      save_output.append(position)

  # Save remaining items
  print(f"{len(save_output)} Items remaining. Saving file...")
  with open("bot_agents.json", "w") as f:
    json.dump(save_output, f)