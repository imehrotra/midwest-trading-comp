#author Dope Trading Group

from algo_client import *
from pprint import pprint
from vollib import black_scholes as b_s
import greeks_new.py as g

def ourOrderBook(algo_client):

	algo_name = "Case 2 Trial"

	#getting the book
	book = algo_client.getOrderBook()

	if book:
		for key in book:
			book.get(key,None)

def priceAndGreekData(algo_client):
	instrument1 = algo_client.getExchangeInstrument(contract_name = "ESM7")
	instrument2 = algo_client.getExchangeInstrument(contract_name = "ESN7")
	instrument3 = algo_client.getExchangeInstrument(contract_name = "ESQ7")
	instrument4 = algo_client.getExchangeInstrument(contract_name = "ESU7")

	market_depth1 = algo_client.getMarketData(instrument1)
	market_depth2 = algo_client.getMarketData(instrument2)
	market_depth3 = algo_client.getMarketData(instrument3)
	market_depth4 = algo_client.getMarketData(instrument4)

	trade_data1 = algo_client.getTradeData(instrument1)
	trade_data2 = algo_client.getTradeData(instrument2)
	trade_data3 = algo_client.getTradeData(instrument3)
	trade_data4 = algo_client.getTradeData(instrument4)

	if market_depth1["bids"]

#TODO
#1. Pick an option/price (python API)

#2. Back out implied volatility (vollib)
#vollib.black_scholes.implied_volatility.implied_volatility(price, S, K, t, r, flag)
#it's in greeks calculator!
def back_out(CallPutFlag, price, underlying, strike, time_to_expiry, interest):
	return g.implied_vol(CallPutFlag, price, underlying, strike, time_to_expiry, interest)
#how do I get the inputs, need to access market and trade data...wait it does it for me so just take it from what greeks outputs...
#ok so now how do I use given greeks calculator

#3. Take IV and calculate theoretical price of other options (vollib)
	return b_s.black_scholes(flag, S, K, t, r, sigma)
#4. Find differences between actual option price and theoretical (math/coding)

#5. Make market (greatest->least) (TBD)

#6. Hedge 


