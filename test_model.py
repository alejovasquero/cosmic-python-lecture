from datetime import date, timedelta
import pytest

from model import Batch, OrderLine, Product, Order

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch =  Batch(reference="BT001", sku="0001", quantity=20)

    line = OrderLine(id="OL001", product=None, quantity=4)

    batch.allocate(line=line)

    assert batch.quantity == 16


def test_can_allocate_if_available_greater_than_required():
    batch =  Batch(reference="BT001", sku="0001", quantity=1000)

    line = OrderLine(id="OL001", product=None, quantity=400)

    batch.allocate(line=line)

    assert batch.quantity == 600


def test_cannot_allocate_if_available_smaller_than_required():
    batch =  Batch(reference="BT001", sku="0001", quantity=1000)

    line = OrderLine(id="OL001", product=None, quantity=1001)

    batch.allocate(line=line)

    assert batch.quantity == 1000


def test_can_allocate_if_available_equal_to_required():
    batch =  Batch(reference="BT001", sku="0001", quantity=1000)

    line = OrderLine(id="OL001", product=None, quantity=1000)

    batch.allocate(line=line)

    assert batch.quantity == 0


def test_prefers_warehouse_batches_to_shipments():
    pytest.fail("todo")


def test_prefers_earlier_batches():
    pytest.fail("todo")
