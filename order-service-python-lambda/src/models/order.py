"""Domain model for an order.

The dataclass performs no I/O; persistence is handled by the repository and the
DynamoDB integration.
"""

from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    customer: str
    amount: float

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        return cls(
            order_id=data["order_id"],
            customer=data["customer"],
            amount=float(data["amount"]),
        )

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer": self.customer,
            "amount": self.amount,
        }