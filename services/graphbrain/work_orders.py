from __future__ import annotations


def generate_work_orders(consolidation_candidates: list[dict], risk_findings: list[dict], gaps: list[dict]) -> list[dict]:
    orders: list[dict] = []
    for idx, candidate in enumerate(consolidation_candidates, start=1):
        orders.append(
            {
                "id": f"wo-consolidate-{idx}",
                "assignee": "Agent-Zero",
                "type": "reasoning",
                "summary": (
                    f"Assess consolidation for {candidate['left']} and {candidate['right']} "
                    f"(score={candidate['score']})."
                ),
                "source": candidate,
            }
        )

    for idx, risk in enumerate(risk_findings, start=1):
        orders.append(
            {
                "id": f"wo-risk-{idx}",
                "assignee": "Devika",
                "type": "execution",
                "summary": f"Mitigate risk '{risk['risk']}' in {risk['repo']}.",
                "source": risk,
            }
        )

    for idx, gap in enumerate(gaps, start=1):
        orders.append(
            {
                "id": f"wo-gap-{idx}",
                "assignee": "Devika",
                "type": "execution",
                "summary": f"Close gap '{gap['gap']}' for {gap['repo']}.",
                "source": gap,
            }
        )
    return orders
