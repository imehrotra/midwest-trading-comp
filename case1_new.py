import numpy as np
import statsmodels.api as sm
import time as time
from algo_client import *
import algo_client
algo_client.ENV = "ext-prod-sim"


START_TIME = time.time() #measures time in second

def x_list(x1, x2):
    x_arr=[]
    y_arr=[]
	# store instrument and trade data
	for x in xrange(1,100):
		instrument1 = algo_client.getExchangeInstrument(contract_name = x1)
		trade_data1 = algo_client.getTradeData(instrument)
		ltp1 = trade_data1.ltp
		x_arr[x] = ltp1
		instrument2 = algo_client.getExchangeInstrument(contract_name = x2)
		trade_data2 = algo_client.getTradeData(instrument)
		ltp2 = trade_data2.ltp
		y_arr[x] = ltp2
      	return (x_arr, y_arr)

def lin_reg(x_arr, y_arr):
	X = np.array(x_arr)
	y = np.array(y_arr)
	X = sm.add_constant(X)
	model = sm.OLS(y, X)
	results = model.fit()
	params = results.params
	B = abs(params[1])
	e = abs(params[0])
	std_err = results.bse[1]
	residuals = results.resid
    avg = np.average(residuals)
    
	info_dict = {}
    info_dict['B'] = B
    info_dict['e'] = e
    info_dict['std_err'] = std_err
    info_dict['avg_resid'] = avg
    return info_dict



#get market data, evaluate reg function with lowest price, call spread function on price, call order function with ret val and market data as params
#iterate with time functions 
def eval_reg(beta, epsilon, x1, x2, x2_p, dict_of_dict, algo_client):
	#get time
	start = time.time()
	while((time.time()-start) < 12):
		instrument1 = algo_client.getExchangeInstrument(contract_name = x1)
		market_data = algo_client.getMarketData(instrument1)
		instrument2 = algo_client.getExchangeInstrument(contract_name = x2)

		#get lowest ask price
		asks = market_data['asks']
		price = asks[0]['p']
		for x in range(0,len(asks)):
			p = asks[x]['p']
			if p <  price:
				price = p

		#calculate y
		y = beta*price + epsilon

		ret = market_size(x2_p-y, dict_of_dict["("+x1+","+x2+")"])
		send_order(algo_client, (instrument1, instrument2), ret, market_data)


def z_score_calculator(spread, dict_of_dict):
    return (y_value - dict_of_dict)["avg_resid"] / dict_of_dict["std_err"];
  
#this function will determine the market order size, return (call_num, put_num)
def market_size(spread, dict_of_dict):
    y_target = 0;
    x_target = 0;
    # index 0- sell or buy(False = sell), index 1 =p1, index 2=p2 (False = call)
    action = [True, False, False] 
    z_score = z_score_calculator(spread, dict_of_dict)

    if z_score < (-2):
        y_target = 50
        x_target = 50 * dict_of_dict["B"]
        action[1] = True
        action[2] = False
    elif z_score > (-1):
        y_target = 20
        x_target = 20 * dict_of_dict["B"]
        action[1] = True
        action[2] = False
    elif z_score > (2):
        y_target = 50
        x_target = 50 * dict_of_dict["B"]
        action[1] = False
        action[2] = True
    elif z_score < (1):
        y_target = 20
        x_target = 20 * dict_of_dict["B"]
        action[1] = False
        action[2] = True

    elif z_score < (-.5):
        y_target = 10
        x_target = 10 * dict_of_dict["B"]
        action[1] = True
        action[2] = False
    elif z_score > (.5):
        y_target = 10
        x_target = 10 * dict_of_dict["B"]
        action[1] = True
        action[2] = False 
    
    #sell coniditions
    elif z_score < (.2) or z_score > (-.2):
        action[0] = False

    return (action, int(x_target), int(y_target))

#current_position- False = shorts, True = call
def send_order(algo_client, instruments, order_results, market_data):
    positions = algo_client.getPositions()
    net_positions = positions["net_pos"]
    current_position = 

    if order_results[0]: 
        buyPrice = 5 * (market_data["asks"][0]["p"] + market_data["asks"][1]["p"])
        parameter1 = {"BaseQty": order_results[1], "AddlQty": order_results[1] // 10, "OrderPrice": buyPrice, "Instr":instruments[0]}      
        order = algo_client.sendOrder(algo_name, parameter1, side = Side.Buy)
        sellPrice = 5 * (market_data["bids"][0]["p"] + market_data["bids"][1]["p"])
        parameter2 = {"BaseQty": order_results[1], "AddlQty": order_results[1] // 10, "OrderPrice": buyPrice, "Instr":instruments[1]}      
        order = algo_client.sendOrder(algo_name, parameter2, side = Side.Sell)
    else:
        buyPrice = 5 * (market_data[instruments[0]["bids"][0]["p"] + market_data["bids"][1]["p"]) 
        parameter1 = {"BaseQty": order_results[1], "AddlQty": order_results[1] // 10, "OrderPrice": buyPrice, "Instr":instruments[0]}      
        order = algo_client.sendOrder(algo_name, parameter1, side = Side.Buy)
        sellPrice = 5 * (market_data["bids"][0]["p"] + market_data["bids"][1]["p"])
        parameter2 = {"BaseQty": order_results[1], "AddlQty": order_results[1] // 10, "OrderPrice": buyPrice, "Instr":instruments[1]}      
        order = algo_client.sendOrder(algo_name, parameter2, side = Side.Sell)
    #current positions need to be bought/balanced
    elif order_rusults[0] == True and order_results[0] != current_position:
        buyPrice = 5 * (market_data["asks"][0]["p"] + market_data["asks"][1]["p"])
        parameters = {"BaseQty": order_results[1], "AddlQty": order_results[1] // 10, "OrderPrice": buyPrice, "Instr":instrument[0]}      
        order = algo_client.sendOrder(algo_name, parameters, side = Side.Buy)
    #current positions need to be sold
    elif order_rusults[0] == False and order_results[0] != current_position:
        sellPrice = 5 * (market_data["bids"][0]["p"] + market_data["bids"][1]["p"])
        parameters = {"BaseQty": order_results[1], "AddlQty": order_results[1] // 10, "OrderPrice": sellPrice, "Instr":instrument[0]}      
        order = algo_client.sendOrder(algo_name, parameters, side = Side.Sell)



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
	#while (time.time() - time_start) < 900: 
	#	theoreticalPricer(algo_client)
	#	orderExecutor(algo_client)
		##hedger(algo_client)
      
    
#get market data, evaluate reg function with lowest price, call spread function on price, call order function with ret val and market data as params
#first will write main function structure and data structs then do above stuff
#iterate with time functions   
	products = ["ZFM7", "ZNM7"] #, "ZBM7", "ESM7"]

	length = len(products)
	dict_of_dict = {}
	#num = 0
	#beta_list = []
	max_beta = 0
	epsilon = 0

  	for x in range(0, length):
  		for y in range(x, length):
	    	ltp_tuple = x_list(products[x], products[y])
	    	info_dict = lin_reg(ltp_tuple[0], ltp_tuple[1])
	    	dict_of_dict["("+products[x]+","+products[y]+")"] = info_dict
	    	#num+=1
			#beta_list.append((info_dict['B'],info_dict['e'])

			#need highest beta and corresponding e
			if info_dict['B'] > max_beta:
				max_beta = info_dict['B']
				epsilon = info_dict['e']
				x1 = products[x]
				x2 = products[y]
				x2_p = ltp_tuple[1]

	#beta_list.sort()

	eval_reg(max_beta, epsilon, x1, x2, x2_p, dict_of_dict, algo_client)
    #now call new func with iterating market data

    