from datetime import date

from src.edtech_cost_service import CourseDelivery, CourseDeliveryRequest


def main() -> None:
    request = CourseDeliveryRequest(
        course_id="algebra-101",
        learner_id="learner-42",
        lesson="Explain one practical use of linear equations in two sentences.",
        deadline=date(2026, 9, 30),
        report_to="educator-report",
    )
    receipt = CourseDelivery().deliver(request)
    print(receipt.report)
    print({"deadline": receipt.due.isoformat(), "cost_usd": receipt.cost_usd})


if __name__ == "__main__":
    main()

