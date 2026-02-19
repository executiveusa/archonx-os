# Access Kernel Quickstart (5 minutes)

## 1) Start stack

```bash
docker compose up --build
```

## 2) Login (mock mode)

```bash
python cli/archonxctl/main.py login --principal pauli --principal-type human --duration 60
```

## 3) Upload secrets JSON

```bash
python cli/archonxctl/main.py secrets upload --file ops/demo/demo-secrets.json --principal pauli --work-item-id WI-1001
```

## 4) Request + approve a grant

```bash
python cli/archonxctl/main.py grants request --principal pauli --principal-type human --resource github --action write --duration 30 --work-item-id WI-1001
python cli/archonxctl/main.py grants list
python cli/archonxctl/main.py grants approve --grant-id <grant_id> --approver admin --work-item-id WI-1001
```

## 5) Export audit evidence

```bash
python cli/archonxctl/main.py audit export --output ops/reports/access-kernel_audit.jsonl
curl http://localhost:8090/v1/evidence/export
```

## 6) Simulate voice action

```bash
curl -X POST http://localhost:8091/v1/voice/dev/simulate \
  -H "Content-Type: application/json" \
  -d '{"caller":"+15550000001","passphrase":"archonx-passphrase","pin":"1234","action":"status","work_item_id":"WI-1001"}'
```
