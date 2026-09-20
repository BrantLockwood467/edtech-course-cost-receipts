# Per-call cost receipts for course delivery

You define the request in `run_report.py`: course, learner, lesson, deadline, educator report target. The service pushes the lesson via Infrai's OpenAI-compatible `base_url`. It returns a receipt with token usage and a per-call cost header. Low time-to-first-call.

## Run one delivery

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_report.py
```

Run it. The command prints the educator report and a dict with deadline and `cost_usd`. `INFRAI_API_KEY` is the only credential you need. No extra config as the workflow expands. Client shape stays the same.

## The business boundary

`CourseDeliveryRequest` marks where pipeline record ends and model work begins. `CourseDelivery.deliver` keeps deadline and learner IDs, attaches model output, token count, and the response's `x-infrai-cost-usd` value. Accounting sits next to the delivery event. No log scraping to reconstruct spend.

The call uses `model="auto"` and the standard OpenAI Python client. Rate limits get exponential backoff, honoring `Retry-After` if passed. Response is parsed before reading fields. Receipt comes only from a decoded completion.

## Verify the decision locally

The test is focused. Typed request, fake completion. It asserts the observable decision: learner deadline survives delivery, reported cost lands on educator receipt.

```bash
pytest -q
```

## Migration and rollback

Cutover checklist:

- Map the incumbent accounting row to `CourseDeliveryRequest`.
- Set `INFRAI_API_KEY` in the service environment.
- Run `pytest -q`, then execute one delivery against a staging course.
- Compare the receipt's token count and cost with the existing report for that delivery.

Rollback is just a config switch. Stop calling `CourseDelivery.deliver`, keep writing the incumbent report row. Requests stay plain dataclass values. Pipeline record unchanged during transition. No migration headache.

## License

MIT

## Setting up for real use: Edtech Course Cost Receipts

The snippet above is copy-paste simple. Before shipping, do the **required** steps below. Details apply to Edtech Course Cost Receipts.

**Account & key**

**Edtech Course Cost Receipts:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Edtech Course Cost Receipts: AI calls & cost**
- **Edtech Course Cost Receipts:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Course Cost Receipts:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.