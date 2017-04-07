###############################################################################
#
#                    Unpublished Work Copyright (c) 2017
#                  Trading Technologies International, Inc.
#                       All Rights Reserved Worldwide
#
#          # # #   S T R I C T L Y   P R O P R I E T A R Y   # # #
#
# WARNING:  This program (or document) is unpublished, proprietary property
# of Trading Technologies International, Inc. and is to be maintained in
# strict confidence. Unauthorized reproduction, distribution or disclosure
# of this program (or document), or any program (or document) derived from
# it is prohibited by State and Federal law, and by local law outside of
# the U.S.
#
###############################################################################

__author__ = 'llazzara'

from algo_client import *
from pprint import pprint
import time


def orderBookExample(algo_client):

    algo_name = "ES_ALGO_00"

    # get order book as dict {order_id: {execution_report}}
    book = algo_client.getOrderBook()

    if book:
        # lookup by order_id
        order_id = "111"  # provide valid order_id
        er = book.get(order_id, None)

    # locate working algo order using a query
    # locate parent order via 'security_desc': <algo.algo_name>
    # locate child order via 'parent_order_id': <algo.order_id>
    ers = algo_client.getOrderBook(query={"security_desc": algo_name, "synth_status": 3}) # may return multiple matches, refine search as needed
    if ers:
        er = ers[0]
        order1 = Order(**er)  # create order object from a resting order in the book
        algo_client.changeOrder(order1, user_parameters={"BaseQty": 12})  # modify user_parameter for a working algo

def priceDataExample(algo_client):

    instrument = algo_client.getExchangeInstrument(contract_name="ESM7")  # future
    # instrument = algo_client.getExchangeInstrument(contract_name="ESM7", strike="P9700")  # option

    # get market depth for an instrument, callback function will receive all price updates for the instrument
    market_depth = algo_client.getMarketData(instrument)
    pprint(market_depth)

    trade_data = algo_client.getTradeData(instrument)
    pprint(trade_data)

    # extract price and qty from market_depth
    if market_depth["bids"]:
        best_bid_price = market_depth["bids"][0]["p"]
    if market_depth["asks"]:
        best_ask_qty = market_depth["asks"][0]["q"]

def sendAlgoOrderExample(algo_client):

    # add an algo instrument to the algo client
    algo_name = "ES_ALGO_00"
    algo_client.addAlgoInstrument(algo_name)

    # retrieve algo user parameters
    algo_parameters = algo_client.getUserParameters(algo_name)
    print("[{} user_parameters]".format(algo_name))
    pprint(algo_parameters)

    # retrieve algo export value parameters
    algo_exportValues = algo_client.getExportValues(algo_name)
    print("[{} export values]".format(algo_name))
    pprint(algo_exportValues)

    # get instrument object
    instrument = algo_client.getExchangeInstrument(contract_name="ESM7")

    # start price subscription for an instrument, will also get price updates in callback function
    market_depth = algo_client.getMarketData(instrument)

    # submit an algo order - any modifiable parameter can be specified via user_parameters, instrument accounts must be assigned in the algo
    # all execution reports will be sent to the callback function
    order = algo_client.sendOrder(algo_name, user_parameters={"BaseQty": 15, "AddlQty": 5, "OrderPrice": 236600, "Instr": instrument.instrumentId}, side=Side.Buy)

    # retrieve current value of export values
    export_values = algo_client.getExportValues(algo_name)
    pprint(export_values)

    time.sleep(2)

    if order.cum_qty == order.order_qty:
        # change algo order in working state
        algo_client.changeOrder(order, user_parameters={"BaseQty": 25, "PriceFlag": True})
    else:
        # change algo order in working state
        algo_client.changeOrder(order, user_parameters={"BaseQty": 8, "PriceFlag": True})

    time.sleep(2)

    algo_client.pauseOrder(order)

    time.sleep(2)

    # change algo order in paused state
    algo_client.changeOrder(order, user_parameters={"BaseQty": 20, "PriceFlag": False})

    time.sleep(2)

    algo_client.resumeOrder(order)

    time.sleep(2)

    algo_client.deleteOrder(order)

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

    username = "your_ttid@email.com"
    password = "your_password"

    algo_client = Algo_Client(username, password)

    # register callbacks functions, a separate thread will be create for each callback type
    algo_client.registerCallbacks(CallbackTypes.Orders, process_orders)
    algo_client.registerCallbacks(CallbackTypes.Prices, process_prices)
    algo_client.registerCallbacks(CallbackTypes.Positions, process_positions, timeout=0.1)

    priceDataExample(algo_client)

    sendAlgoOrderExample(algo_client)

    bbook = algo_client.getBookieOrderBook()

    # retrieve account positions, will also receive all account instrument positions in the callback function
    positions = algo_client.getPositions()

    # deleted/filled orders will remain in the book, need to check exec_type attribute (3=Cancelled, 4=Replaced, 14=Traded)
    book = algo_client.getOrderBook()


