from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from opentariff.Enums.base_enums import DayOfWeek
from opentariff.Enums.tariff_enums import TariffEnums


class StandingCharge(BaseModel):
    tcr_band: TariffEnums.TCRBand
    tcrbandtype: TariffEnums.TCRBandType
    max_consumption: Decimal
    min_consumption: Decimal
    line_loss: Decimal
    value: Decimal


class Rate(BaseModel):
    """Unified rate model for all rate types"""

    model_config = ConfigDict(frozen=True)

    rate_type: TariffEnums.RateType
    unit_rate: Decimal = Field(..., gt=0, lt=100)

    # Fields for time-of-use static rates
    time_from: Optional[time] = None
    time_to: Optional[time] = None
    day_from: Optional[DayOfWeek] = None
    day_to: Optional[DayOfWeek] = None
    month_from: Optional[int] = Field(None, ge=1, le=12)
    month_to: Optional[int] = Field(None, ge=1, le=12)

    # Fields for dynamic rates
    rate_datetime: Optional[datetime] = None

    @field_validator("time_to")
    @classmethod
    def validate_time_to(cls, v: Optional[time], info) -> Optional[time]:
        if v and info.data.get("time_from") and v == info.data["time_from"]:
            raise ValueError("time_to must not equal time_from")
        return v

    @field_validator("day_to")
    @classmethod
    def validate_day_to(cls, v: Optional[time], info) -> Optional[time]:
        if v and info.data.get("day_from") and v == info.data["day_from"]:
            raise ValueError("day_to must not equal day_from")
        return v

    @field_validator("month_to")
    @classmethod
    def validate_month_to(cls, v: Optional[int], info) -> Optional[int]:
        if v and info.data.get("month_from") and v == info.data["month_from"]:
            raise ValueError("month_to must not equal to month_from")
        return v

    @field_validator("rate_type")
    @classmethod
    def validate_rate_fields(
        cls, v: TariffEnums.RateType, info
    ) -> TariffEnums.RateType:
        """Validate that required fields are present based on rate type"""
        if v == TariffEnums.RateType.TIME_OF_USE_STATIC:
            if not all(
                [
                    info.data.get("time_from"),
                    info.data.get("time_to"),
                    info.data.get("month_from"),
                    info.data.get("month_to"),
                ]
            ):
                raise ValueError(
                    "time_of_use_static rates require time_from, time_to, month_from, and month_to"
                )
        elif v == TariffEnums.RateType.TIME_OF_USE_DYNAMIC:
            if not info.data.get("rate_datetime"):
                raise ValueError("time_of_use_dynamic rates require rate_datetime")
        return v


class Tariff(BaseModel):
    """Core tariff information"""

    model_config = ConfigDict(frozen=True)

    dno_region: int = Field(..., ge=10, le=23)
    rate_type: TariffEnums.RateType
    fuel_type: TariffEnums.Fuel
    payment_method: TariffEnums.PaymentMethod
    contract_length_months: Optional[int] = Field(None, gt=0)
    contract_end_date: Optional[date] = None
    on_supply_from: Optional[datetime] = None
    on_supply_to: Optional[datetime] = None
    exit_fee_type: Optional[TariffEnums.ExitFeeType] = None
    exit_fee_value: Optional[Decimal] = Field(None, ge=0)
    supplier_name: Optional[str] = None
    supplier_tariff_code: Optional[str] = None
    standing_charges: list[StandingCharge]
    rates: list[Rate]

    @field_validator("rates")
    @classmethod
    def validate_rates(cls, v: list[Rate], info) -> list[Rate]:
        if not v:
            raise ValueError("tariff must have at least one rate")
        if "rate_type" in info.data:
            for rate in v:
                if rate.rate_type != info.data["rate_type"]:
                    raise ValueError("all rates must match tariff rate_type")
        return v

    @field_validator("exit_fee_value")
    @classmethod
    def validate_exit_fee(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        if v is not None and not info.data.get("exit_fee_type"):
            raise ValueError(
                "exit_fee_type is required when exit_fee_value is provided"
            )
        return v
