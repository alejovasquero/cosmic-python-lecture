import abc
import model
from sqlalchemy import text, CursorResult


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        if not self._validate_batch_exists(batch=batch):
            self.session.execute(
                text(
                    f"INSERT INTO batches(reference, sku, eta, _purchased_quantity) VALUES (:reference, :sku, :eta, :_purchased_quantity)"
                ),
                {
                    "reference": batch.reference,
                    "sku": batch.sku,
                    "eta": batch.eta,
                    "_purchased_quantity": batch._purchased_quantity,
                },
            )

        batch_id: CursorResult = self.session.execute(
            text(f"SELECT id FROM batches WHERE reference = :reference"),
            {
                "reference": batch.reference,
            },
        )

        batch_id = batch_id.fetchone()[0]

        print(batch_id)

        for line in batch._allocations:
            self._insert_line_if_not_exists(line)
            print("VALIDATING ORDER LINE")
            print(line.__dict__)
            if not self._validate_allocated_line(batch, line):
                print("ALLOCATING NEW ORDER LINE")
                print(line.orderid, batch_id)
                self.session.execute(
                    text(
                        "INSERT INTO allocations(orderline_id, batch_id) "
                        + "SELECT id as orderline_id, :batch_id as batch_id FROM order_lines WHERE orderid = :orderid"
                    ),
                    {
                        "orderid": line.orderid,
                        "batch_id": batch_id,
                    },
                )

        self.session.commit()

    def _insert_line_if_not_exists(self, order_line: model.OrderLine) -> None:
        count_cursor: CursorResult = self.session.execute(
            text(f"SELECT COUNT(*) FROM order_lines WHERE orderid = :orderid"),
            {
                "orderid": order_line.orderid,
            },
        )

        count = count_cursor.fetchone()[0]

        if count == 0:
            self.session.execute(
                text(
                    f"INSERT INTO order_lines(sku, qty, orderid) VALUES (:sku, :qty, :orderid)"
                ),
                {
                    "sku": order_line.sku,
                    "qty": order_line.qty,
                    "orderid": order_line.orderid,
                },
            )
            self.session.commit()

    def _validate_batch_exists(self, batch: model.Batch) -> bool:
        cursor: CursorResult = self.session.execute(
            text(
                "SELECT COUNT(*) FROM batches AS b " + "WHERE b.reference = :reference"
            ),
            {"reference": batch.reference},
        )
        result = cursor.fetchone()

        return result[0] == 1

    def _validate_allocated_line(
        self, batch: model.Batch, order_line: model.OrderLine
    ) -> bool:
        cursor: CursorResult = self.session.execute(
            text(
                "SELECT COUNT(*) FROM allocations AS a "
                + "INNER JOIN batches AS b ON a.batch_id = b.id "
                + "INNER JOIN order_lines AS ord_lines ON ord_lines.id = a.orderline_id "
                + "WHERE ord_lines.orderid = :orderid AND b.reference = :reference"
            ),
            {"orderid": order_line.orderid, "reference": batch.reference},
        )
        result = cursor.fetchone()
        print(result)

        assert result[0] < 2
        return result[0] == 1

    def get(self, reference) -> model.Batch:
        cursor: CursorResult = self.session.execute(
            text(
                "SELECT b.id, b.reference, b.sku, b._purchased_quantity, b.eta FROM batches AS b WHERE b.reference = :reference"
            ),
            {"reference": reference},
        )

        batch = cursor.fetchone()

        if batch == None:
            return None

        batch = batch._asdict()

        cursor_lines: CursorResult = self.session.execute(
            text(
                "SELECT ord.id, ord.sku, ord.qty, ord.orderid FROM order_lines AS ord INNER JOIN allocations AS alc ON alc.orderline_id = ord.id WHERE alc.batch_id = :reference"
            ),
            {"reference": batch["id"]},
        )

        lines = cursor_lines.fetchall()

        result_entity = model.Batch(
            ref=batch["reference"],
            eta=batch["eta"],
            qty=batch["_purchased_quantity"],
            sku=batch["sku"],
        )

        for line in lines:
            parsed_line = model.OrderLine(sku=line[1], qty=line[2], orderid=line[3])
            result_entity.allocate(parsed_line)

        return result_entity
