from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from robinhood_client.common.enums import (
    CurrencyCode,
    OrderType,
    OrderSide,
    OrderState,
    PositionEffect,
    TimeInForce,
    TriggerType,
)


class Currency(BaseModel):
    """Represents a currency amount with its code and identifier."""

    amount: str | float
    """The monetary amount."""

    currency_code: CurrencyCode | str
    """The currency code (e.g., 'USD', 'EUR')."""

    currency_id: str
    """The unique identifier for the currency."""


class StockOrderExecution(BaseModel):
    """Represents an execution of a stock order."""

    price: str | float
    """The execution price per share."""

    quantity: str | float
    """The number of shares executed."""

    rounded_notional: str | float
    """The rounded notional value of the execution."""

    settlement_date: date | str
    """The settlement date for the execution."""

    timestamp: datetime | str
    """The timestamp when the execution occurred."""

    id: str
    """The unique identifier for the execution."""

    ipo_access_execution_rank: Optional[str] = None  # TODO: Confirm type
    """The IPO access execution rank."""

    trade_execution_date: date | str
    """The date when the trade was executed."""

    fees: str | float
    """The total fees for the execution."""

    sec_fee: Optional[str | float] = None
    """The SEC fee for the execution."""

    taf_fee: Optional[str | float] = None
    """The TAF (Trading Activity Fee) for the execution."""

    cat_fee: Optional[str | float] = None
    """The CAT (Consolidated Audit Trail) fee for the execution."""

    sales_taxes: List[str | float]  # TODO: Confirm type
    """The sales taxes applied to the execution."""


class StockOrder(BaseModel):
    """Represents a stock order."""

    id: str
    """The unique identifier for the order."""

    ref_id: str
    """The reference identifier for the order."""

    url: str
    """The URL for the order details."""

    account: str
    """The account associated with the order."""

    user_uuid: str
    """The unique identifier for the user."""

    position: str
    """The position associated with the order."""

    cancel: Optional[str] = None  # TODO: Confirm type
    """The cancellation URL or identifier."""

    instrument: str
    """The instrument URL for the stock."""

    instrument_id: str
    """The unique identifier for the instrument."""

    cumulative_quantity: str | float
    """The cumulative quantity filled."""

    average_price: Optional[str | float]
    """The average price of filled shares."""

    fees: str | float
    """The total fees for the order."""

    sec_fees: str | float
    """The SEC fees for the order."""

    taf_fees: str | float
    """The TAF (Trading Activity Fee) for the order."""

    cat_fees: str | float
    """The CAT (Consolidated Audit Trail) fees for the order."""

    sales_taxes: List[str | float]  # TODO: Confirm type
    """The sales taxes applied to the order."""

    state: OrderState
    """The current state of the order."""

    derived_state: OrderState
    """The derived state of the order."""

    pending_cancel_open_agent: Optional[str] = None  # TODO: Confirm type
    """The pending cancel open agent."""

    type: OrderType
    """The type of the order."""

    side: OrderSide
    """The side of the order (buy/sell)."""

    time_in_force: TimeInForce
    """The time in force for the order."""

    trigger: TriggerType
    """The trigger type for the order."""

    price: Optional[str | float] = None
    """The price per share for the order."""

    stop_price: Optional[str | float] = None
    """The stop price for the order."""

    quantity: Optional[str | float] = None
    """The quantity of shares for the order."""

    reject_reason: Optional[str] = None  # TODO: Confirm type
    """The reason the order was rejected."""

    created_at: datetime | str
    """The timestamp when the order was created."""

    updated_at: datetime | str
    """The timestamp when the order was last updated."""

    last_transaction_at: datetime | str
    """The timestamp of the last transaction."""

    executions: List[StockOrderExecution]
    """The list of executions for the order."""

    extended_hours: bool
    """Whether the order is for extended hours trading."""

    market_hours: str  # TODO: Convert to Enum
    """The market hours for the order (e.g., 'regular_hours')."""

    override_dtbp_checks: bool
    """Whether to override day trading buying power checks."""

    override_day_trade_checks: bool
    """Whether to override day trade checks."""

    response_category: Optional[str] = None  # TODO: Confirm type
    """The response category for the order."""

    stop_triggered_at: Optional[datetime | str] = None  # TODO: Confirm type
    """The timestamp when the stop was triggered."""

    last_trail_price: Optional[str | float] = None
    """The last trail price for trailing stop orders."""

    last_trail_price_updated_at: Optional[datetime | str] = None  # TODO: Confirm type
    """The timestamp when the trail price was last updated."""

    last_trail_price_source: Optional[str] = None  # TODO: Confirm type
    """The source of the last trail price."""

    dollar_based_amount: Optional[Currency] = None
    """The dollar-based amount for the order when bought based on dollars."""

    total_notional: Optional[Currency] = None
    """The total notional value of the order."""

    executed_notional: Optional[Currency] = None
    """The executed notional value of the order."""

    investment_schedule_id: Optional[str] = None
    """The investment schedule identifier."""

    is_ipo_access_order: bool
    """Whether this is an IPO access order."""

    ipo_access_cancellation_reason: Optional[str] = None  # TODO: Confirm type
    """The reason for IPO access order cancellation."""

    ipo_access_lower_collared_price: Optional[str | float] = None
    """The lower collared price for IPO access."""

    ipo_access_upper_collared_price: Optional[str | float] = None
    """The upper collared price for IPO access."""

    ipo_access_upper_price: Optional[str | float] = None
    """The upper price for IPO access."""

    ipo_access_lower_price: Optional[str | float] = None
    """The lower price for IPO access."""

    is_ipo_access_price_finalized: bool
    """Whether the IPO access price is finalized."""

    is_visible_to_user: bool
    """Whether the order is visible to the user."""

    has_ipo_access_custom_price_limit: bool
    """Whether the IPO access has a custom price limit."""

    is_primary_account: bool
    """Whether this is the primary account."""

    order_form_version: int
    """The version of the order form (e.g., 6)."""

    preset_percent_limit: Optional[str | float] = None
    """The preset percent limit for the order."""

    order_form_type: str
    """The type of order form (e.g., 'share_based_market_buys')."""

    last_update_version: int
    """The last update version (e.g., 2)."""

    placed_agent: str
    """The agent that placed the order (e.g., 'user')."""

    is_editable: bool
    """Whether the order is editable."""

    replaces: Optional[str] = None  # TODO: Confirm type
    """The order that this order replaces."""

    user_cancel_request_state: str  # TODO: Convert to Enum
    """The user cancel request state (e.g., 'order_finalized')."""

    tax_lot_selection_type: Optional[str] = None  # TODO: Confirm type
    """The tax lot selection type."""

    position_effect: Optional[PositionEffect] = None
    """The position effect for the order."""


class StockOrdersPageResponse(BaseModel):
    """Response model for paginated stock orders."""

    results: List[StockOrder]
    """List of stock orders."""

    next: Optional[str] = None
    """URL for the next page of results, if any."""

    previous: Optional[str] = None
    """URL for the previous page of results, if any."""

    count: Optional[int] = None
    """Total count of orders across all pages."""


class OptionsOrderExecution(BaseModel):
    """Represents an execution within an options order leg."""

    id: str
    """The unique identifier for the execution."""

    price: str | float
    """The execution price per contract."""

    quantity: str | float
    """The number of contracts executed."""

    settlement_date: date | str
    """The settlement date for the execution."""

    timestamp: datetime | str
    """The timestamp when the execution occurred."""


class OptionsOrderLeg(BaseModel):
    """Represents a leg of an options order."""

    id: str
    """The unique identifier for the order leg."""

    option: str
    """URL to the option instrument."""

    position_effect: str  # TODO: Convert to Enum
    """The position effect ('open' or 'close')."""

    ratio_quantity: int
    """The ratio quantity for the leg."""

    side: str  # TODO: Convert to Enum
    """The side of the leg ('buy' or 'sell')."""

    expiration_date: date | str
    """The expiration date of the option."""

    strike_price: str | float
    """The strike price of the option."""

    option_type: str  # TODO: Convert to Enum
    """The type of option ('call' or 'put')."""

    long_strategy_code: str
    """The long strategy code for the leg."""

    short_strategy_code: str
    """The short strategy code for the leg."""

    executions: List[OptionsOrderExecution]
    """The list of executions for this leg."""


class OptionsOrder(BaseModel):
    """Represents an options order."""

    id: str
    """The unique identifier for the options order."""

    ref_id: str
    """The reference identifier for the options order."""

    account_number: str
    """The Robinhood account number associated with the order."""

    cancel_url: Optional[str] = None
    """CONFIRM: The URL to cancel the options order."""

    canceled_quantity: str | float
    """The quantity of the options order that has been canceled."""

    created_at: datetime | str
    """The timestamp when the options order was created."""

    direction: str  # TODO: Convert to Enum
    """The direction of the options order, either 'credit' or 'debit'."""

    legs: List[OptionsOrderLeg]
    """The legs of the options order."""

    pending_quantity: str | float
    """The quantity of the options order that is still pending."""

    premium: str | float
    """The premium amount for the options order."""

    processed_premium: str | float
    """The processed premium amount for the options order."""

    processed_premium_direction: str  # TODO: Convert to Enum
    """The direction of the processed premium, either 'credit' or 'debit'."""

    net_amount: str | float
    """The net amount for the options order."""

    net_amount_direction: str  # TODO: Convert to Enum
    """The direction of the net amount, either 'credit' or 'debit'."""

    price: str | float
    """The price per unit for the options order."""

    processed_quantity: str | float
    """The quantity of the options order that has been processed."""

    quantity: str | float
    """The total quantity for the options order."""

    regulatory_fees: str | float
    """The regulatory fees associated with the options order."""

    contract_fees: str | float
    """The contract fees associated with the options order."""

    gold_savings: str | float
    """The gold savings amount associated with the options order."""

    state: OrderState
    """The current state of the options order."""

    time_in_force: TimeInForce
    """The time in force for the options order."""

    trigger: TriggerType
    """The trigger type for the options order."""

    type: OrderType
    """The type of the options order."""

    updated_at: datetime | str
    """The timestamp when the options order was last updated."""

    chain_id: str
    """The unique identifier for the options chain."""

    chain_symbol: str
    """The underlying stock symbol for the options chain."""

    response_category: Optional[str] = None
    """CONFIRM: The response category for the options order."""

    opening_strategy: Optional[str] = None
    """The opening strategy for the options order."""

    closing_strategy: Optional[str] = None
    """The closing strategy for the options order."""

    stop_price: Optional[str | float] = None
    """The stop price for the options order."""

    form_source: Optional[str] = None
    """The source of the order form."""

    client_bid_at_submission: Optional[str | float] = None
    """The client bid price at the time of order submission."""

    client_ask_at_submission: Optional[str | float] = None
    """The client ask price at the time of order submission."""

    client_time_at_submission: Optional[datetime | str] = None
    """The client time at the time of order submission."""

    average_net_premium_paid: Optional[str | float] = None
    """The average net premium paid for the options order."""

    estimated_total_net_amount: Optional[str | float] = None
    """The estimated total net amount for the options order."""

    estimated_total_net_amount_direction: Optional[str] = None
    """The direction of the estimated total net amount, either 'credit' or 'debit'."""

    is_replaceable: bool
    """Indicates if the options order is replaceable."""

    strategy: Optional[str] = None  # TODO: Convert to Enum
    """ The strategy of the options order."""

    derived_state: OrderState
    """The derived state of the options order."""

    sales_taxes: List[str | float]
    """The sales taxes associated with the options order."""


class OptionsOrdersPageResponse(BaseModel):
    """Response model for paginated options orders."""

    results: List[OptionsOrder]
    """List of options orders."""

    next: Optional[str] = None
    """URL for the next page of results, if any."""

    previous: Optional[str] = None
    """URL for the previous page of results, if any."""
