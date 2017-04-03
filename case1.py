#1.build a yield curve through finding the implied yield(100-price)
#2.calculate the derived yield by measuring needed interest rate between 1-yr treasury future and 5-yr treasury future
#3.take a position on the yield curve -if the derived yield is greater 
#than the interest rate, then steepening yeild curve (buy near contract and sell far contract )
#4. Hedge by making sure the dollar value of 1% change in the yield of the short term future equals that of the long term (DV01)


from algo_client import *
import math

