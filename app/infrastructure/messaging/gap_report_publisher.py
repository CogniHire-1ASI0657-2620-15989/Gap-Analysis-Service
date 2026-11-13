import json
import uuid
from datetime import UTC, datetime

import aio_pika

from app.domain.model.aggregates.gap_report import GapReport
from app.observability import configure_logging, get_correlation_id


class GapReportPublisher:
    """Publishes non-critical events without affecting the HTTP request outcome."""

    EXCHANGE = "pathbridge.events"
    ROUTING_KEY = "gap_report.generated"
    QUEUE = "learning-pathway.gap-report"
    RETRY_EXCHANGE = "pathbridge.retry"
    RETRY_QUEUE = "learning-pathway.gap-report.retry"
    DEAD_LETTER_EXCHANGE = "pathbridge.dead-letter"
    DEAD_LETTER_QUEUE = "learning-pathway.gap-report.dlq"

    def __init__(self, rabbitmq_url: str | None):
        self._rabbitmq_url = rabbitmq_url
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None
        self._logger = configure_logging("gap-analysis-service")

    async def publish(self, report: GapReport) -> None:
        if not self._rabbitmq_url:
            self._logger.info("event_publish_skipped", extra={"event_type": self.ROUTING_KEY})
            return
        try:
            exchange = await self._get_exchange()
            body = {
                "event_id": str(uuid.uuid4()),
                "event_type": self.ROUTING_KEY,
                "occurred_at": datetime.now(UTC).isoformat(),
                "correlation_id": get_correlation_id(),
                "user_id": report.user_id,
                "job_id": report.job_id,
                "gap_report_id": report.id,
                "missing_hard_skills": [skill.name for skill in report.missing_hard_skills],
            }
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(body).encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    message_id=body["event_id"],
                    correlation_id=body["correlation_id"],
                    type=body["event_type"],
                ),
                routing_key=self.ROUTING_KEY,
            )
            self._logger.info("event_published", extra={"event_type": self.ROUTING_KEY})
        except Exception:
            self._logger.exception("event_publish_failed", extra={"event_type": self.ROUTING_KEY})

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None

    async def _get_exchange(self) -> aio_pika.abc.AbstractExchange:
        if self._exchange is not None:
            return self._exchange
        self._connection = await aio_pika.connect_robust(self._rabbitmq_url)
        self._channel = await self._connection.channel(publisher_confirms=True)
        self._exchange = await self._channel.declare_exchange(
            self.EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
        )
        retry_exchange = await self._channel.declare_exchange(
            self.RETRY_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True
        )
        dead_letter_exchange = await self._channel.declare_exchange(
            self.DEAD_LETTER_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await self._channel.declare_queue(
            self.QUEUE,
            durable=True,
            arguments={"x-dead-letter-exchange": self.DEAD_LETTER_EXCHANGE},
        )
        await queue.bind(self._exchange, routing_key=self.ROUTING_KEY)
        retry_queue = await self._channel.declare_queue(
            self.RETRY_QUEUE,
            durable=True,
            arguments={
                "x-message-ttl": 30000,
                "x-dead-letter-exchange": self.EXCHANGE,
                "x-dead-letter-routing-key": self.ROUTING_KEY,
            },
        )
        await retry_queue.bind(retry_exchange, routing_key=self.QUEUE)
        dead_letter_queue = await self._channel.declare_queue(self.DEAD_LETTER_QUEUE, durable=True)
        await dead_letter_queue.bind(dead_letter_exchange, routing_key=self.ROUTING_KEY)
        return self._exchange
