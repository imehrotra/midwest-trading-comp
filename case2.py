#author Dope Trading Group

from algo_client import *
from pprint import pprint
from vollib import black

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





