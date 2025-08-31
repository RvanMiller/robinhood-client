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
    amount: str | float
    currency_code: CurrencyCode | str
    currency_id: str


class StockOrderExecution(BaseModel):
    price: str | float
    quantity: str | float
    rounded_notional: str | float
    settlement_date: date | str
    timestamp: datetime | str
    id: str
    ipo_access_execution_rank: Optional[str] = None  # TODO: Confirm type
    trade_execution_date: date | str
    fees: str | float
    sec_fee: Optional[str | float] = None
    taf_fee: Optional[str | float] = None
    cat_fee: Optional[str | float] = None
    sales_taxes: List[str | float]  # TODO: Confirm type


class StockOrder(BaseModel):
    """Represents a stock order.

    Args:
        id (str): The unique identifier for the order.
        ref_id (str): The reference identifier for the order.
        url (str): The URL for the order details.
        dollar_based_amount (NotionalCurrency): The dollar-based amount for the order when
            Stock is bought based on Dollars and not number of Shares.

    """

    id: str
    ref_id: str
    url: str
    account: str
    user_uuid: str
    position: str
    cancel: Optional[str] = None  # TODO: Confirm type
    instrument: str
    instrument_id: str
    cumulative_quantity: str | float
    average_price: Optional[str | float]
    fees: str | float
    sec_fees: str | float
    taf_fees: str | float
    cat_fees: str | float
    sales_taxes: List[str | float]  # TODO: Confirm type
    state: OrderState
    derived_state: OrderState
    pending_cancel_open_agent: Optional[str] = None  # TODO: Confirm type
    type: OrderType
    side: OrderSide
    time_in_force: TimeInForce
    trigger: TriggerType
    price: Optional[str | float] = None
    stop_price: Optional[str | float] = None
    quantity: Optional[str | float] = None
    reject_reason: Optional[str] = None  # TODO: Confirm type
    created_at: datetime | str
    updated_at: datetime | str
    last_transaction_at: datetime | str
    executions: List[StockOrderExecution]
    extended_hours: bool
    market_hours: str  # e.g. "regular_hours"
    override_dtbp_checks: bool
    override_day_trade_checks: bool
    response_category: Optional[str] = None  # TODO: Confirm type
    stop_triggered_at: Optional[datetime | str] = None  # TODO: Confirm type
    last_trail_price: Optional[str | float] = None
    last_trail_price_updated_at: Optional[datetime | str] = None  # TODO: Confirm type
    last_trail_price_source: Optional[str] = None  # TODO: Confirm type
    dollar_based_amount: Optional[Currency] = None
    total_notional: Optional[Currency] = None
    executed_notional: Optional[Currency] = None
    investment_schedule_id: Optional[str] = None
    is_ipo_access_order: bool
    ipo_access_cancellation_reason: Optional[str] = None  # TODO: Confirm type
    ipo_access_lower_collared_price: Optional[str | float] = None
    ipo_access_upper_collared_price: Optional[str | float] = None
    ipo_access_upper_price: Optional[str | float] = None
    ipo_access_lower_price: Optional[str | float] = None
    is_ipo_access_price_finalized: bool
    is_visible_to_user: bool
    has_ipo_access_custom_price_limit: bool
    is_primary_account: bool
    order_form_version: int  # e.g. 6
    preset_percent_limit: Optional[str | float] = None
    order_form_type: str  # e.g. "share_based_market_buys"
    last_update_version: int  # e.g. 2
    placed_agent: str  # e.g. "user"
    is_editable: bool
    replaces: Optional[str] = None  # TODO: Confirm type
    user_cancel_request_state: str  # e.g. "order_finalized"
    tax_lot_selection_type: Optional[str] = None  # TODO: Confirm type
    position_effect: Optional[PositionEffect] = None


class StockOrdersPageResponse(BaseModel):
    """Response model for paginated stock orders."""

    results: List[StockOrder]
    next: Optional[str] = None
    previous: Optional[str] = None
    count: Optional[int] = None
