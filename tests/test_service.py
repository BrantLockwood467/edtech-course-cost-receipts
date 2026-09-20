from datetime import date
from types import SimpleNamespace

from src.edtech_cost_service import CourseDelivery, CourseDeliveryRequest


class FakeRaw:
    headers = {"x-infrai-cost-usd": "0.12"}

    def parse(self):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Use a budget equation."))],
            usage=SimpleNamespace(total_tokens=17),
        )


class FakeCompletions:
    @property
    def with_raw_response(self):
        return self

    def create(self, **kwargs):
        assert kwargs["model"] == "auto"
        assert kwargs["messages"][0]["content"]
        return FakeRaw()


class FakeClient:
    chat = SimpleNamespace(completions=FakeCompletions())


def test_delivery_receipt_contains_deadline_and_cost():
    req = CourseDeliveryRequest("algebra-101", "learner-42", "Explain equations.", date(2026, 9, 30), "educator-report")
    receipt = CourseDelivery(FakeClient()).deliver(req)
    assert receipt.due == date(2026, 9, 30)
    assert receipt.cost_usd == 0.12
    assert "learner-42 received algebra-101" in receipt.report
