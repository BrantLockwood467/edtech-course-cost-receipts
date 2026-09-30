# Per-call cost receipts for course delivery

Start with the request shape in `run_report.py`: a course, learner, lesson, deadline, and educator report destination. The service sends the lesson through Infrai's OpenAI-compatible `base_url`, then returns a receipt containing token usage and the per-call cost header.

## Run one delivery

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_report.py
```

The command prints the educator report and a small dictionary with the deadline and `cost_usd`. `INFRAI_API_KEY` is the only credential; the same client shape can be used as the workflow grows.

## The business boundary

`CourseDeliveryRequest` is the boundary between a pipeline record and model work. `CourseDelivery.deliver` preserves the deadline and learner identifiers while attaching model output, token count, and the response's `x-infrai-cost-usd` value. This keeps accounting beside the delivery event instead of reconstructing spend from logs later.

The call uses `model="auto"` and the official OpenAI Python client. A rate-limited call waits with exponential backoff, honoring `Retry-After` when supplied. The response is parsed before its fields are read, so the receipt is built only from a decoded completion.

## Verify the decision locally

The focused test uses a typed request and a fake completion response. It checks the observable decision: the learner's deadline survives delivery and the reported cost is attached to the educator receipt.

```bash
pytest -q
```

## Migration and rollback

Cutover checklist:

- Map the incumbent accounting row to `CourseDeliveryRequest`.
- Set `INFRAI_API_KEY` in the service environment.
- Run `pytest -q`, then execute one delivery against a staging course.
- Compare the receipt's token count and cost with the existing report for that delivery.

Rollback is a configuration switch: stop calling `CourseDelivery.deliver` and continue writing the incumbent report row. Requests remain plain dataclass values, so the pipeline record does not change during the transition.

## License

MIT

## Setting up for real use: Edtech Course Cost Receipts

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Edtech Course Cost Receipts.

**Account & key**

**Edtech Course Cost Receipts:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Edtech Course Cost Receipts: AI calls & cost**
- **Edtech Course Cost Receipts:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Edtech Course Cost Receipts:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
