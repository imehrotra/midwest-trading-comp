from algo_client import *
import vollib.black_scholes.implied_volatility as iv
import vollib.black.greeks.numerical as num
import math

#calculates delta
#CallPutFlag: if 1 then call, 0 if put
def delta(CallPutFlag,S,X,T,r,v):
    if CallPutFlag == 1:
        return num.delta('c', S, X, T, r, v)
    else:
        return num.delta('p', S, X, T, r, v)

#vega is the same for calls and puts
#CallPutFlag: if 1 then call, 0 if put
def vega(CallPutFlag,S,X,T,r,v):
    if CallPutFlag == 1:
        return num.vega('c', S/float(100), X/float(100), T, r, v)
    else:
        return num.vega('p', S/float(100), X/float(100), T, r, v)

#simple implied volatility approximation
#CallPutFlag: if 1 then call, 0 if put
def implied_vol(CallPutFlag, price, underlying, strike, time_to_expiry, interest):
    if CallPutFlag == 1:
        return iv.implied_volatility(price, underlying, strike, time_to_expiry, interest, 'c')
    else:
        return iv.implied_volatility(price, underlying, strike, time_to_expiry, interest, 'p')

class Greeks(object):

    def __init__(self, algo_client, contract, strikes, interest, time_to_expiry):
        self.algo_client = algo_client
        self.strikes = strikes
        self.contract = contract
        self.time_to_expiry = time_to_expiry
        self.delta = {strike: [0,0] for strike in self.strikes}
        self.vega = {strike: [0,0] for strike in self.strikes}
        self.interest = interest
        self.implied_vol = {strike: [.1,.1] for strike in strikes}

        self.calls = {strike: algo_client.getExchangeInstrument(contract_name=self.contract, strike='C'+str(strike/100)) for strike in self.strikes}
        self.puts = {strike: algo_client.getExchangeInstrument(contract_name=self.contract, strike='P'+str(strike/100)) for strike in self.strikes}
        self.underlying = algo_client.getExchangeInstrument(contract_name=self.contract)
        self.update_implied_vol()
        self.update_delta()
        self.update_vega()

    def update_implied_vol(self):
        for strike in self.strikes:
            market_depth_call = self.algo_client.getMarketData(self.calls[strike], display=False)
            underlying = self.algo_client.getMarketData(self.underlying, display=False)
            if market_depth_call["bids"] and market_depth_call["asks"] and underlying["bids"] and underlying["asks"]:
                underlying_midpoint = (underlying["bids"][0]["p"] + underlying["asks"][0]["p"])/2.
                call_midpoint = (market_depth_call["bids"][0]["p"] + market_depth_call["asks"][0]["p"])/2
                self.implied_vol[strike][0] = implied_vol(1, call_midpoint, underlying_midpoint, strike, self.time_to_expiry, self.interest)

            market_depth_put = self.algo_client.getMarketData(self.puts[strike], display=False)
            if market_depth_put["bids"] and market_depth_put["asks"] and underlying["bids"] and underlying["asks"]:
                underlying_midpoint = (underlying["bids"][0]["p"] + underlying["asks"][0]["p"])/2.
                put_midpoint = (market_depth_put["bids"][0]["p"] + market_depth_put["asks"][0]["p"])/2
                self.implied_vol[strike][1] = implied_vol(0, put_midpoint, underlying_midpoint, strike, self.time_to_expiry, self.interest)


    def update_delta(self):
        #underlying = 24000
        self.update_implied_vol()
        for strike in self.strikes:
            underlying = self.algo_client.getMarketData(self.underlying, display=False)
            if underlying["bids"] and underlying["asks"]:
                underlying_midpoint = (underlying["bids"][0]["p"] + underlying["asks"][0]["p"])/2.

                call_vol = self.implied_vol[strike][0]
                self.delta[strike][0] = delta(1, strike, underlying_midpoint, self.time_to_expiry, self.interest, call_vol)

                put_vol = self.implied_vol[strike][1]
                self.delta[strike][1] = delta(0, strike, underlying_midpoint, self.time_to_expiry, self.interest, put_vol)

    def update_vega(self):
        #underlying = 24000
        self.update_implied_vol()
        for strike in self.strikes:
            underlying = self.algo_client.getMarketData(self.underlying, display=False)
            if underlying["bids"] and underlying["asks"]:
                underlying_midpoint = (underlying["bids"][0]["p"] + underlying["asks"][0]["p"])/2.

                call_vol = self.implied_vol[strike][0]
                self.vega[strike][0] = vega(1, strike, underlying_midpoint, self.time_to_expiry, self.interest, call_vol)

                put_vol = self.implied_vol[strike][1]
                self.vega[strike][1] = vega(0, strike, underlying_midpoint, self.time_to_expiry, self.interest, put_vol)

    def log_prices(self):
        underlying = self.algo_client.getMarketData(self.underlying, display=False)
        underlying_midpoint = (underlying["bids"][0]["p"] + underlying["asks"][0]["p"])/2.
        log.info("UNDERLYING MIDPOINT: {}".format(underlying_midpoint))
        for strike in self.strikes:
            market_depth_call = self.algo_client.getMarketData(self.calls[strike], display=False)
            market_depth_put = self.algo_client.getMarketData(self.puts[strike], display=False)
            call_midpoint = (market_depth_call["bids"][0]["p"] + market_depth_call["asks"][0]["p"])/2
            put_midpoint = (market_depth_put["bids"][0]["p"] + market_depth_put["asks"][0]["p"])/2
            log.info("  CALL MIDPOINT: {}   PUT MIDPOINT: {}".format(call_midpoint, put_midpoint))


    def log_greeks(self):
        self.update_implied_vol()
        self.update_delta()
        self.update_vega()
        log.info("IMPLIED VOL")
        for strike in self.strikes:
            log.info("  C{}/P{}: {}".format(strike, strike, self.implied_vol[strike]))
        log.info("DELTA")
        for strike in self.strikes:
            log.info("  C{}: {}, P{}:{}".format(strike, self.delta[strike][0], strike, self.delta[strike][1]))
        log.info("VEGA")
        for strike in self.strikes:
            log.info("  C{}: {}, P{}:{}".format(strike, self.vega[strike][0], strike, self.vega[strike][1]))

    def return_delta(self):
        self.update_delta()
        return self.delta

    def return_vega(self):
        self.update_vega()
        return self.vega

    def return_implied_vol(self):
        self.update_implied_vol()
        return self.implied_vol



