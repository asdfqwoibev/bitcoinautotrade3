import time
import pyupbit
import datetime
import requests
import schedule

access = ""        # 본인 값으로 변경
secret = ""
DISCORD_WEBHOOK_URL = ''

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)
    
def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
send_message("자동매매 시작")
schedule.every().day.at("11:00").do(send_message, "작동 중")

while True:
    schedule.run_pending()
    time.sleep(1)
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=2)
        stop_price = df.iloc[0]['close']
        if start_time < now < end_time - datetime.timedelta(seconds=60):
            target_price = get_target_price("KRW-BTC", 0.3)
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price :
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    send_message("매수" +str(buy_result))
            elif current_price == stop_price :
                BTC = get_balance("BTC")
                if BTC > 0.00008:
                    sell_result = upbit.sell_market_order("KRW-BTC", BTC*0.9995)
                    send_message( "매도" +str(sell_result))                
        else:
            BTC = get_balance("BTC")
            if BTC > 0.00008:
                sell_result = upbit.sell_market_order("KRW-BTC", BTC*0.9995)
                send_message( "매도" +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        send_message(e)
        time.sleep(1)
