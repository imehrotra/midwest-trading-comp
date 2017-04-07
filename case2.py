#author Dope Trading Group
from algo_client import *
from pprint import pprint
from vollib import black_scholes as b_s
from greeks_new import Greeks
#import greeks_new.py as g
from datetime import datetime
import algo_client
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

def impliedVolList(algo_client):
##########################################################################################
	given_strikes = ["C2200", "P2200", "C2225", "P2225", "C2175", "P2175"]
	options = []
	iv_list = []
	#get last traded price
	ltp = trade_data['ltp']
	for x in xrange(1,6):
		strikes = {}

		# store instrument and trade data
		strike_numstr = given_strikes[x]
		instrument = algo_client.getExchangeInstrument(contract_name = "ESM7", strike = strike_numstr)
		trade_data = algo_client.getTradeData(instrument)
		strikes['instrument'] = instrument
		strikes['trade_data'] = trade_data
		options[x-1] = strikes #is this right?


		#get call put flag
		flag = strike_numstr[0]
		#get strike price
		strike_price = strike_numstr[1:]

		#calculate time to expiry (use py time funcs)
#<<<<<<< HEAD
#		time = trade_data['time']
#		date_format = "%Y-%m-%d"
#		curr_date = datetime.strptime(time, date_format)
#		expiry = datetime(2017, 6, 16)
#		date_diff = expiry - curr_date
#		time_to_expiry = date_diff.days/365.0
#=======
		tToE = time_to_expiry()


		#get underlying price


		#solve for implied vol and store in list
		iv = g.implied_vol(flag, ltp, 2300, strike_price, tToE, 0.01)
		iv_list[x-1] = iv
##########################################################################################
#<<<<< HEAD
	calls = []
	puts = []

	given_strikes = [2340, 2345, 2350, 2355, 2360, 2365, 2370, 2375, 2380]
	interest = .01
	time_to_expiry = 70/252
	greeks = Greeks(algo_client, "ESM7", given_strikes, interest, time_to_expiry)
	iv = greeks.return_implied_vol()
	strike = given_strikes[x]
	calls[x] = iv[strike][0]
	puts[x] = iv[strike][1]

	#do i need underlying

	deltas = greeks.return_delta()
	call_delta = deltas[2380][0]
#=======

def theoreticalPricer(algo_client):
	for x in xrange(1,6):
		strike_numstr = given_strikes[x]
		strikePrice[x-1] = strike_numstr[1:]
	greeks = Greeks(algo_client,"ESM7", strikePrice,.01, time_to_expiry())
	deltas = g.return_delta()
	vegas = g.return_vega()
	for x in xrange(1,6):
		if strike_numstr[0] == 'C':
			flag = 0
		else:
			flag = 1
		delta =  deltas[strike_numstr[1:]][flag]
		vega = vegas[strike_numstr[1:]][flag]
		if flag == 0:
			CPflag = 'c'
		else:
			CPflag == 'p'
		theoreticalPrice[x-1] = b_s.black_scholes(CPflag,2300,strikePrice[x-1],time_to_expiry(),.01,iv_list[x-1])

def orderExecutor(algo_client):
	
	algo_name = "shitty algorithm"
	algo_client.addAlgoInsturment(algo_name)
	algo_parameters = algo_client.getUserParameters(algo_name)
	algo_exportValues = algo_client.getExportValues(algo_name)
	market_depth = algo_client.getMarketData(instrument)

	if market_depth["bids"]:
		best_bid_price = market_depth["bids"][0]["p"]
		best_bid_qty = market_depth["bids"][0]["q"]
	if market_depth["asks"]:
		best_ask_price = market_depth["asks"][0]["p"]
		best_ask_qty = market_depth["asks"][0]["q"]

	for x in xrange(1,6):
		if theoreticalPrice[x-1] < best_bid_price:
			buyPrice = (best_bid_price + best_ask_price)/2 + theoreticalPrice[x-1] / 2 - .25
			order = algo_client.sendOrder(algo_name, userparameters = {"BaseQty": 40, "AddlQty": 5, "OrderPrice": buyPrice, "Instr":instrument.instrumentId}, side = Side.Buy )
		if theoreticalPrice[x-1] > best_ask_price:
			sellPrice= (best_bid_price + best_ask_price)/2 + theoreticalPrice[x-1] / 2 + .25
			order = algo_client.SendOrder(algo_name, userparameters = {"BaseQty": 40, "AddlQty": 5, "OrderPrice": sellPrice, "Instr": instrument.instrumentId}, side = Side.Sell)
#def hedger(algo_client):
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
		print(data)
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
	print(data)
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

	impliedVolList(algo_client)
	theoreticalPricer(algo_client)
	orderExecutor(algo_client)

	bbook = algo_client.getBookieOrderBook()

    # retrieve account positions, will also receive all account instrument positions in the callback function
	positions = algo_client.getPositions()

    # deleted/filled orders will remain in the book, need to check exec_type attribute (3=Cancelled, 4=Replaced, 14=Traded)
	book = algo_client.getOrderBook()



