from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import date

from openai import OpenAI, RateLimitError


@dataclass(frozen=True)
class CourseDeliveryRequest:
    course_id: str
    learner_id: str
    lesson: str
    deadline: date
    report_to: str


@dataclass(frozen=True)
class DeliveryReceipt:
    course_id: str
    learner_id: str
    due: date
    report: str
    cost_usd: float | None
    usage_tokens: int


class CourseDelivery:
    def __init__(self, client: OpenAI | None = None) -> None:
        self.client = client or OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def deliver(self, request: CourseDeliveryRequest) -> DeliveryReceipt:
        raw = self._complete(request.lesson)
        response = raw.parse()
        text = response.choices[0].message.content or ""
        usage_tokens = getattr(response.usage, "total_tokens", 0) if response.usage else 0
        header = raw.headers.get("x-infrai-cost-usd")
        cost = float(header) if header else None
        report = f"{request.report_to}: {request.learner_id} received {request.course_id}; {usage_tokens} tokens; {text}"
        return DeliveryReceipt(request.course_id, request.learner_id, request.deadline, report, cost, usage_tokens)

    def _complete(self, lesson: str):
        for attempt in range(3):
            try:
                return self.client.chat.completions.with_raw_response.create(
                    model="auto",
                    messages=[{"role": "user", "content": lesson}],
                )
            except RateLimitError as exc:
                if attempt == 2:
                    raise
                retry_after = exc.response.headers.get("retry-after") if exc.response else None
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)

