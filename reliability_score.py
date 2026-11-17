
def calculate_reliability(results):

    if not results:
        return {
            "reliability_score": 0,
            "supported": 0,
            "contradicted": 0,
            "insufficient": 0,
            "total_claims": 0
        }

    supported = 0
    contradicted = 0
    insufficient = 0

    for item in results:

        result = item.get("result", "")

        if result == "Supported":
            supported += 1

        elif result == "Contradicted":
            contradicted += 1

        else:
            insufficient += 1

    total_claims = len(results)

    verifiable_claims = supported + contradicted

    if verifiable_claims == 0:
        score = 0
    else:
        score = round(
            (supported / verifiable_claims) * 100,
            2
        )

    return {
        "reliability_score": score,
        "supported": supported,
        "contradicted": contradicted,
        "insufficient": insufficient,
        "total_claims": total_claims
    }
