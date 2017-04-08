#author Dope Trading Group
from algo_client import *
from pprint import pprint
from vollib import black_scholes as b_s
from greeks_new import Greeks
#import greeks_new.py as g
from datetime import datetime
import time


def ourOrderBook(algo_client):

	algo_name = "CASE2 Algorithm"

	#getting the book
	book = algo_client.getOrderBook()

	if book:
		for key in book:
			book.get(key,None)


def timeToExpiry(algo_client):
	time = trade_data['time']
	date_format = "%Y-%m-%d"
	curr_date = datetime.strptime(time, date_format)
	expiry = datetime(2017, 6, 16)
	delta = expiry - curr_date
	time_to_expiry = delta/365
	return time_to_expiry


def theoreticalPricer(algo_client):
	calls = []
	puts = []
	given_strikes = [233500, 234000, 234500,235000,235500]
	strikes = ["C2335", "P2335", "C2340", "P2340", "C2345","P2345","C2350","P2350","C2355","P2355"] 
	interest = .01
	time_to_expiry = float(60/252)
	greeks = Greeks(algo_client, "ESM7", given_strikes, .01, .24)
	iv = greeks.return_implied_vol()
	for x in xrange(1,3):
		calls.append(iv[given_strikes[x-1]][0])
		puts.append(iv[given_strikes[x-1]][1])
	theoreticalPrice = {}
	x = 0
	while x < 5: 
		theoreticalPrice[strikes[x]] = b_s.black_scholes('c',9830,given_strikes[x/2],.24,.01,calls[x/2])
		theoreticalPrice[strikes[x+1]] = b_s.black_scholes('p',9830.5,given_strikes[x/2], .24,.01,puts[x/2])
		x += 2
	return theoreticalPrice
		

def orderExecutor(algo_client):
	strikes = ["C2335", "P2335", "C2340", "P2340", "C2345","P2345","C2350","P2350","C2355","P2355"]
	algo_name = "CASE2 algorithm"
	algo_client.addAlgoInstrument(algo_name)
	algo_parameters = algo_client.getUserParameters(algo_name)
	algo_exportValues = algo_client.getExportValues(algo_name)
	instrument = {}
	for x in xrange(1,6):
		instrument[strikes[x-1]] = algo_client.getExchangeInstrument(contract_name = "ESM7", strike = strikes[x-1])
		instrument[strikes[x-1]] = algo_client.getExchangeInstrument(contract_name = "ESM7", strike = strikes[x-1])
	market_depth = {}
	for x in xrange(1,6):
		market_depth.update({strikes[x-1]:algo_client.getMarketData(instrument[strikes[x-1]])})

	algo_parameters = algo_client.getUserParameters(algo_name)
	algo_exportValues = algo_client.getExportValues(algo_name)

	best_bid_price = {}
	best_bid_qty = {}
	best_ask_price = {}
	best_ask_qty = {}
	for x in xrange(1,3):
		if market_depth[strikes[x-1]]["bids"]:
			best_bid_price[strikes[x-1]] = market_depth[strikes[x-1]]["bids"][0]["p"]
			best_bid_qty[strikes[x-1]] = market_depth[strikes[x-1]]["bids"][0]["q"]
		if market_depth[strikes[x-1]]["asks"]:
			best_ask_price[strikes[x-1]] = market_depth[strikes[x-1]]["asks"][0]["p"]
			best_ask_qty[strikes[x-1]] = market_depth[strikes[x-1]]["asks"][0]["q"]

	theoretical_Price = theoreticalPricer(algo_client)
	x = 0
	for key,value in theoretical_Price.iteritems():
		if value > best_ask_price[key]:
			order = algo_client.sendOrder(algo_name, user_parameters = {"BaseQty": best_ask_qty[key], "OrderPrice": best_ask_price[key],"Instr": instrument[key].instrumentId}, side = Side.Buy )
		if value < best_bid_price[key]:
			order = algo_client.sendOrder(algo_name, user_parameters = {"BaseQty": best_bid_qty[key], "OrderPrice": best_bid_price[key],"Instr": instrument[key].instrumentId}, side = Side.Sell )

##def hedger(algo_client):
#	position = algo_client.getPositions()

#	for key, value in position.iteritems():
#		if value != None:
#			given_strikes

def process_orders(name, data):

    # callback for Execution report and export value messages

	if "ExecutionReport" in name:
		log.info("{} order_id={} side={} price={} qty={} last_qty={} exec_type={} ord_status={}".format(name, data["order_id"], data.get("side", None), data.get("price", None), data.get("order_qty", None), data.get("last_qty", None), data.get("exec_type", None), data.get("ord_status", None) ))
	else:
		log.info("{} callback".format(name))
		#print(data)
    # pprint(data)  # pretty formatting

def process_prices(name, data):

    # callback for MarketDepth and TradeData messages

	log.info("{} callback for instrument_id={}".format(name, data["instrument_id"]))

	if data.get("asks", None) is not None and data["asks"]:
		log.info("   Inside Ask {} x {}".format(data["asks"][0]["q"], data["asks"][0]["p"]))
	if data.get("bids", None) is not None and data["bids"]:
		log.info("   Inside Bid {} x {}".format(data["bids"][0]["q"], data["bids"][0]["p"]))

    # print(data)
    # pprint(data)  # pretty formatting

def process_positions(name, data):

    # callback for PositionsUpdate and PositionsDelete messages

	log.info("{} callback".format(name))
	#print(data)
    # pprint(data)  # pretty formatting


if __name__ == "__main__":

    # a valid account must be specified in the instrument block, no support to change the account
    # does not support user-defined data types
    # algo field must be defined as user_defined in order to modify them

	username = "mtcjhouse@gmail.com"
	password = "jannotta2017!"

	algo_client = Algo_Client(username, password, es_ip = "uofc-edge-ext-prod-delayed.debesys.net")

    # register callbacks functions, a separate thread will be create for each callback type
	algo_client.registerCallbacks(CallbackTypes.Orders, process_orders)
	algo_client.registerCallbacks(CallbackTypes.Prices, process_prices)
	algo_client.registerCallbacks(CallbackTypes.Positions, process_positions, timeout=0.1)
	time_start = time.time()
	while (time.time() - time_start) < 900: 
		orderExecutor(algo_client)
		##hedger(algo_client)


	bbook = algo_client.getBookieOrderBook()

    # retrieve account positions, will also receive all account instrument positions in the callback function
	positions = algo_client.getPositions()

    # deleted/filled orders will remain in the book, need to check exec_type attribute (3=Cancelled, 4=Replaced, 14=Traded)
	book = algo_client.getOrderBook()




