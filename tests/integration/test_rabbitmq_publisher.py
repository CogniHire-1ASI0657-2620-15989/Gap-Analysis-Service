import json
import os
from datetime import UTC, datetime

import aio_pika
import pytest

from app.domain.model.aggregates.gap_report import GapReport
from app.domain.model.value_objects.skill_gap import SkillGap
from app.infrastructure.messaging.gap_report_publisher import GapReportPublisher


@pytest.mark.asyncio
async def test_publishes_gap_report_event_to_rabbitmq() -> None:
    rabbitmq_url = os.getenv("RABBITMQ_URL")
    if not rabbitmq_url:
        pytest.skip("RABBITMQ_URL is required for this integration test.")

    publisher = GapReportPublisher(rabbitmq_url)
    connection = await aio_pika.connect_robust(rabbitmq_url)
    try:
        await publisher._get_exchange()  # Arrange the same durable topology used in production.
        channel = await connection.channel()
        queue = await channel.declare_queue(
            GapReportPublisher.QUEUE,
            durable=True,
            arguments={"x-dead-letter-exchange": GapReportPublisher.DEAD_LETTER_EXCHANGE},
        )
        await queue.purge()
        now = datetime.now(UTC)
        report = GapReport(
            id=987,
            user_id=123,
            job_id=456,
            job_title="Backend Developer",
            job_description_snippet=None,
            match_percentage=50,
            matched_hard_skills=[],
            missing_hard_skills=[SkillGap(name="Docker", skill_type="hard")],
            matched_soft_skills=[],
            missing_soft_skills=[],
            analysis_source="test",
            analysis_status="completed",
            analysis_engine="rules",
            created_at=now,
            updated_at=now,
        )

        await publisher.publish(report)
        message = await queue.get(timeout=5, fail=False)
        assert message is not None
        body = json.loads(message.body)
        assert body["event_type"] == "gap_report.generated"
        assert body["user_id"] == 123
        assert body["job_id"] == 456
        assert body["missing_hard_skills"] == ["Docker"]
        await message.ack()
    finally:
        await publisher.close()
        await connection.close()
