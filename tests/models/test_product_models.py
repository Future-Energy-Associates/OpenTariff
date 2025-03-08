import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from opentariff.models.product_models import Product
from opentariff.Enums.product_enums import ProductEnums


def test_validate_available_to():
    """Test the field validator for available_to date in Product model"""
    # Setup - create base dates for testing
    now = datetime.now()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)
    
    # Test 1: Valid case - available_to is after available_from
    valid_product = Product(
        name="Valid Product",
        domestic=True,
        type=ProductEnums.TariffType.FIXED,
        available_from=now,
        available_to=future
    )
    assert valid_product.available_to == future
    
    # Test 2: Valid case - available_to is None (no end date)
    no_end_product = Product(
        name="No End Date Product",
        domestic=True,
        type=ProductEnums.TariffType.FIXED,
        available_from=now,
        available_to=None
    )
    assert no_end_product.available_to is None
    
    # Test 3: Invalid case - available_to is before available_from
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Invalid Product",
            domestic=True,
            type=ProductEnums.TariffType.FIXED,
            available_from=now,
            available_to=past
        )
    # Verify the error message
    assert "available_to must be after available_from" in str(exc_info.value)
    
    # Test 4: Invalid case - available_to is equal to available_from
    with pytest.raises(ValidationError) as exc_info:
        Product(
            name="Same Date Product",
            domestic=True, 
            type=ProductEnums.TariffType.FIXED,
            available_from=now,
            available_to=now
        )
    # Verify the error message
    assert "available_to must be after available_from" in str(exc_info.value)