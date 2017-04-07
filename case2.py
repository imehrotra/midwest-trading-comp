#author Dope Trading Group
from algo_client import *
from pprint import pprint
from vollib import black_scholes as b_s
from greeks_new import Greeks
#import greeks_new.py as g
from datetime import datetime
import algo_client
import time
algo_client.ENV = "ext-prod-sim"

def ourOrderBook(algo_client):

	algo_name = "Case 2 Trial"

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
	given_strikes = [234000, 234500, 235000, 235500, 236000, 236500, 237000, 237500, 238000]
	interest = .01
	time_to_expiry = float(70/252)
	greeks = Greeks(algo_client, "ESM7", given_strikes, .01, time_to_expiry)
	iv = greeks.return_implied_vol()
	for x in xrange(1,3):
		calls.append(iv[given_strikes[x-1]][0])
		puts.append(iv[given_strikes[x-1]][1])
	theoreticalPrice = {}
	for x in xrange(1,3): 
		theoreticalPrice[ "C" + str(given_strikes[x-1])] = b_s.black_scholes('c',230000,given_strikes[x-1],time_to_expiry,.01,calls[x-1])
		theoreticalPrice[ "P" + str(given_strikes[x-1])] = b_s.black_scholes('p',230000,given_strikes[x-1], time_to_expiry,.01,puts[x-1])
	return theoreticalPrice
		

def orderExecutor(algo_client):
	given_strikes = [234000, 234500, 235000, 235500, 236000, 236500, 237000, 237500, 238000]
	algo_name = "shitty algorithm"
	algo_client.addAlgoInstrument(algo_name)
	instrument = {}
	for x in xrange(1,3):
		instrument["C" + str(given_strikes[x-1])] = algo_client.getExchangeInstrument(contract_name = "ESM7", strike = "C" + str(given_strikes[x-1]))
		instrument["P" + str(given_strikes[x-1])] = algo_client.getExchangeInstrument(contract_name = "ESM7", strike = "P" + str(given_strikes[x-1]))
	market_depth = {}
	for key in instrument.iteritems(): 
		market_depth[key] = algo_client.getMarketData(instrument[key])

	algo_parameters = algo_client.getUserParameters(algo_name)
	algo_exportValues = algo_client.getExportValues(algo_name)

	best_bid_price = {}
	best_bid_qty = {}
	best_ask_price = {}
	best_ask_qty = {}
	for key in market_depth.iteritems():
		if market_depth[key]["bids"]:
			best_bid_price[key] = market_depth[key]["bids"][0]["p"]
			best_bid_qty[key] = market_depth[key]["bids"][0]["q"]
		if market_depth[key]["asks"]:
			best_ask_price = market_depth[key]["asks"][0]["p"]
			best_ask_qty = market_depth[key]["asks"][0]["q"]

	theoretical_Price = theoreticalPricer(algo_client)
	for key in theoretical_Price.iteritems():
		if theoretical_Price[key] < best_bid_price[key]:
			buyPrice = (best_bid_price + best_ask_price)/2 + theoretical_Price[key] / 2 - .25
			order = algo_client.sendOrder(algo_name, userparameters = {"BaseQty": 40, "AddlQty": 5, "OrderPrice": buyPrice, "Instr":instrument.instrumentId}, side = Side.Buy )
		if theoretical_Price[key] > best_ask_price[key]:
			sellPrice= (best_bid_price + best_ask_price)/2 + theoreticalPrice[x-1] / 2 + .25
			order = algo_client.SendOrder(algo_name, userparameters = {"BaseQty": 40, "AddlQty": 5, "OrderPrice": sellPrice, "Instr": instrument.instrumentId}, side = Side.Sell)

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

	algo_client = Algo_Client(username, password)

    # register callbacks functions, a separate thread will be create for each callback type
	algo_client.registerCallbacks(CallbackTypes.Orders, process_orders)
	algo_client.registerCallbacks(CallbackTypes.Prices, process_prices)
	algo_client.registerCallbacks(CallbackTypes.Positions, process_positions, timeout=0.1)
	time_start = time.time()
	while (time.time() - time_start) < 900: 
		theoreticalPricer(algo_client)
		orderExecutor(algo_client)
		##hedger(algo_client)


	bbook = algo_client.getBookieOrderBook()

    # retrieve account positions, will also receive all account instrument positions in the callback function
	positions = algo_client.getPositions()

    # deleted/filled orders will remain in the book, need to check exec_type attribute (3=Cancelled, 4=Replaced, 14=Traded)
	book = algo_client.getOrderBook()



