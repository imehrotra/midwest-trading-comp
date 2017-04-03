#author Dope Trading Group

from algo_client import *
from pprint import pprint
from vollib import black_scholes as b_s
import greeks_new.py as g
from datetime import datetime


def ourOrderBook(algo_client):

	algo_name = "Case 2 Trial"

	#getting the book
	book = algo_client.getOrderBook()

	if book:
		for key in book:
			book.get(key,None)


def timeToExpiry():
	time = trade_data['time']
	date_format = "%Y-%m-%d"
	curr_date = datetime.strptime(time, date_format)
	expiry = datetime(2017, 6, 16)
	delta = expiry - curr_date
	return time_to_expiry = delta.days/365

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
		tToE = time_to_expiry()

		#get underlying price


		#solve for implied vol and store in list
		iv = g.implied_vol(flag, ltp, 2300, strike_price, tToE, 0.01)
		iv_list[x-1] = iv
##########################################################################################

def theoreticalPricer(l):
	given_strikes = ["C2200", "P2200", "C2225", "P2225", "C2175", "P2175"]
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
		else
			CPflag == 'p'
		theoreticalPrice[x-1] = b_s.black_scholes(CPflag,2300,strikePrice[x-1],time_to_expiry(),.01,iv_list[x-1])

def orderExecutor(algo_client):
	book = algo_client.getOrderBook()

	if book:
		for key in 

        





	# 	curr_year = int(time[:3])
	# 	curr_month = int(time[5:6])
	# 	curr_day = int(time[8:9]) #are these nums right?
	# 	if curr_month > 7:
	# 		year = 2016 - curr_year
	# 	else:
	# 		year = 2017 - curr_year
	# 		month = 6 - curr_month
	# 	year = 2017 - curr_year
	# 	month = 
 # 'time': '2017-02-16 09:29:41.261',

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


