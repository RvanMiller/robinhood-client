"""Contains all the url endpoints for interacting with Robinhood API."""
from .helper import id_for_chain, id_for_stock
from .constants import BASE_API_URL, BASE_NUMMUS_URL, BASE_PHOENIX_URL, \
    BASE_MINERVA_URL, BASE_BONFIRE_URL


# Login
#
def login_url():
    return (f'{BASE_API_URL}/oauth2/token/')


def challenge_url(challenge_id):
    return (f'{BASE_API_URL}/challenge/{challenge_id}/respond/')


# Profiles
#
def account_profile_url(account_number=None):
    if account_number:
        return (f'{BASE_API_URL}/accounts/{account_number}')
    else:
        return (f'{BASE_API_URL}/accounts/?default_to_all_accounts=true')


def basic_profile_url():
    return (f'{BASE_API_URL}/user/basic_info/')


def investment_profile_url():
    return (f'{BASE_API_URL}/user/investment_profile/')


def portfolio_profile_url(account_number=None):
    if account_number:
        return (f'{BASE_API_URL}/portfolios/{account_number}')
    else:
        return (f'{BASE_API_URL}/portfolios/')


def security_profile_url():
    return (f'{BASE_API_URL}/user/additional_info/')


def user_profile_url():
    return (f'{BASE_API_URL}/user/')


def portfolio_historicals_url(account_number):
    return (f'{BASE_API_URL}/portfolios/historicals/{account_number}/')


# Stocks
#
def earnings_url():
    return (f'{BASE_API_URL}/marketdata/earnings/')


def events_url():
    return (f'{BASE_API_URL}/options/events/')


def fundamentals_url():
    return (f'{BASE_API_URL}/fundamentals/')


def historicals_url():
    return (f'{BASE_API_URL}/quotes/historicals/')


def instruments_url():
    return (f'{BASE_API_URL}/instruments/')


def news_url(symbol):
    return (f'{BASE_API_URL}/midlands/news/{symbol}/?')


def popularity_url(symbol):
    return (f'{BASE_API_URL}/instruments/{id_for_stock(symbol)}/popularity/')


def quotes_url():
    return (f'{BASE_API_URL}/quotes/')


def ratings_url(symbol):
    return (f'{BASE_API_URL}/midlands/ratings/{id_for_stock(symbol)}/')


def splits_url(symbol):
    return (f'{BASE_API_URL}/instruments/{id_for_stock(symbol)}/splits/')


# Account
#
def phoenix_url():
    return (f'{BASE_PHOENIX_URL}/accounts/unified')


def positions_url(account_number=None):
    if account_number:
        return (f'{BASE_API_URL}/positions/?account_number={account_number}')
    else:
        return (f'{BASE_API_URL}/positions/')


def banktransfers_url(direction=None):
    if direction == 'received':
        return (f'{BASE_API_URL}/ach/received/transfers/')
    else:
        return (f'{BASE_API_URL}/ach/transfers/')


def cardtransactions_url():
    return (f'{BASE_MINERVA_URL}/history/transactions/')


def unifiedtransfers_url():
    return (f'{BASE_BONFIRE_URL}/paymenthub/unified_transfers/')


def daytrades_url(account):
    return (f'{BASE_API_URL}/accounts/{account}/recent_day_trades/')


def dividends_url():
    return (f'{BASE_API_URL}/dividends/')


def documents_url():
    return (f'{BASE_API_URL}/documents/')


def withdrawl_url(bank_id):
    return (f'{BASE_API_URL}/ach/relationships/{bank_id}/')


def linked_url(id=None, unlink=False):
    if unlink:
        return (f'{BASE_API_URL}/ach/relationships/{id}/unlink/')
    if id:
        return (f'{BASE_API_URL}/ach/relationships/{id}/')
    else:
        return (f'{BASE_API_URL}/ach/relationships/')


def margin_url():
    return (f'{BASE_API_URL}/margin/calls/')


def margininterest_url():
    return (f'{BASE_API_URL}/cash_journal/margin_interest_charges/')


def notifications_url(tracker=False):
    if tracker:
        return (f'{BASE_API_URL}/midlands/notifications/notification_tracker/')
    else:
        return (f'{BASE_API_URL}/notifications/devices/')


def referral_url():
    return (f'{BASE_API_URL}/midlands/referral/')


def stockloan_url():
    return (f'{BASE_API_URL}/accounts/stock_loan_payments/')


def interest_url():
    return (f'{BASE_API_URL}/accounts/sweeps/')


def subscription_url():
    return (f'{BASE_API_URL}/subscription/subscription_fees/')


def wiretransfers_url():
    return (f'{BASE_API_URL}/wire/transfers')


def watchlists_url(name=None, add=False):
    if name:
        return (f'{BASE_API_URL}/midlands/lists/items/')
    else:
        return (f'{BASE_API_URL}/midlands/lists/default/')


# Markets
#
def currency_url():
    return (f'{BASE_NUMMUS_URL}/currency_pairs/')


def markets_url():
    return (f'{BASE_API_URL}/markets/')


def market_hours_url(market, date):
    return (f'{BASE_API_URL}/markets/{market}/hours/{date}/')


def movers_sp500_url():
    return (f'{BASE_API_URL}/midlands/movers/sp500/')


def get_100_most_popular_url():
    return (f'{BASE_API_URL}/midlands/tags/tag/100-most-popular/')


def movers_top_url():
    return (f'{BASE_API_URL}/midlands/tags/tag/top-movers/')


def market_category_url(category):
    return (f'{BASE_API_URL}/midlands/tags/tag/{category}/')


# Options
#
def aggregate_url(account_number):
    if account_number:
        return (f'{BASE_API_URL}/options/aggregate_positions/?account_numbers={account_number}')
    else:
        return (f'{BASE_API_URL}/options/aggregate_positions/')


def chains_url(symbol):
    return (f'{BASE_API_URL}/options/chains/{id_for_chain(symbol)}/')


def option_historicals_url(id):
    return (f'{BASE_API_URL}/marketdata/options/historicals/{id}/')


def option_instruments_url(id=None):
    if id:
        return (f'{BASE_API_URL}/options/instruments/{id}/')
    else:
        return (f'{BASE_API_URL}/options/instruments/')


def option_orders_url(orderID=None, account_number=None, start_date=None):
    url = f'{BASE_API_URL}/options/orders/'
    if orderID:
        url += '{0}/'.format(orderID)
    query_build = []
    if account_number:
        query_build.append(f"account_numbers={account_number}")
    if start_date:
        query_build.append(f"updated_at[gte]={start_date}")

    if query_build:
        for index, value in enumerate(query_build):
            if index == 0:
                url += "?" + value
            else:
                url += "&" + value

    return url


def option_positions_url(account_number):
    if account_number:
        return (f'{BASE_API_URL}/options/positions/?account_numbers={account_number}')
    else:
        return (f'{BASE_API_URL}/options/positions/')


def marketdata_options_url():
    return (f'{BASE_API_URL}/marketdata/options/')


# Pricebook
#
def marketdata_quotes_url(id):
    return (f'{BASE_API_URL}/marketdata/quotes/{id}/')


def marketdata_pricebook_url(id):
    return (f'{BASE_API_URL}/marketdata/pricebook/snapshots/{id}/')


# Crypto
#
def order_crypto_url():
    return (f'{BASE_NUMMUS_URL}/orders/')


def crypto_account_url():
    return (f'{BASE_NUMMUS_URL}/accounts/')


def crypto_currency_pairs_url():
    return (f'{BASE_NUMMUS_URL}/currency_pairs/')


def crypto_quote_url(id):
    return (f'{BASE_API_URL}/marketdata/forex/quotes/{id}/')


def crypto_holdings_url():
    return (f'{BASE_NUMMUS_URL}/holdings/')


def crypto_historical_url(id):
    return (f'{BASE_API_URL}/marketdata/forex/historicals/{id}/')


def crypto_orders_url(orderID=None):
    if orderID:
        return (f'{BASE_NUMMUS_URL}/orders/{orderID}/')
    else:
        return (f'{BASE_NUMMUS_URL}/orders/')


def crypto_cancel_url(id):
    return (f'{BASE_NUMMUS_URL}/orders/{id}/cancel/')


# Orders
#
def cancel_url(url):
    return (f'{BASE_API_URL}/orders/{url}/cancel/')


def option_cancel_url(id):
    return (f'{BASE_API_URL}/options/orders/{id}/cancel/')


def orders_url(orderID=None, account_number=None, start_date=None):
    url = f'{BASE_API_URL}/orders/'
    if orderID:
        url += '{0}/'.format(orderID)

    query_build = []
    if account_number:
        query_build.append(f"account_numbers={account_number}")
    if start_date:
        query_build.append(f"updated_at[gte]={start_date}")

    if query_build:
        for index, value in enumerate(query_build):
            if index == 0:
                url += "?" + value
            else:
                url += "&" + value

    return url
