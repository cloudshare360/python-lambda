"""Data access for orders.

Built on top of the DynamoDB integration. It maps DynamoDB items to/from the
`Order` model and contains no business decisions.
"""

import logging

from src.models.order import Order

logger = logging.getLogger(__name__)


class OrderRepository:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb

    def save(self, order: Order) -> None:
        item = order.to_dict()
        logger.debug("OrderRepository.save item=%s", item)
        self.dynamodb.put_item(item)

    def find_by_id(self, order_id: str) -> Order | None:
        logger.debug("OrderRepository.find_by_id order_id=%s", order_id)
        item = self.dynamodb.get_item({"order_id": order_id})
        if not item:
            return None
        return Order.from_dict(item)