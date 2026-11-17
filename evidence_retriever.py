
import requests
import re
import html
from urllib.parse import quote

BASE_URL = "https://en.wikipedia.org/w/api.php"

HEADERS = {
    "User-Agent": "CollegeReliabilityChecker/1.0 (Educational Project)"
}

# Common words that are not useful for Wikipedia searches
STOP_WORDS = {
    "became", "become", "was", "were", "is", "are",
    "the", "a", "an", "in", "on", "of", "to",
    "and", "for", "from", "by", "with", "has",
    "have", "had", "been", "being", "this", "that"
}


def clean_text(text):
    """Remove HTML formatting and unnecessary spaces."""

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def create_search_query(claim):
    """Extract important words from the claim."""

    words = re.findall(r"\w+", claim.lower())

    important_words = [
        word for word in words
        if word not in STOP_WORDS and len(word) > 1
    ]

    return " ".join(important_words)


def retrieve_evidence(claim):
    """
    Search Wikipedia and retrieve relevant article introductions.
    """

    if not claim or not claim.strip():
        return []

    search_query = create_search_query(claim)

    if not search_query:
        return []

    try:
        # Step 1: Search Wikipedia
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json",
            "srlimit": 10
        }

        response = requests.get(
            BASE_URL,
            params=search_params,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        search_results = response.json().get(
            "query", {}
        ).get("search", [])

        if not search_results:
            return []

        # Step 2: Retrieve article introductions
        selected_results = search_results[:5]

        page_ids = [
            str(result["pageid"])
            for result in selected_results
        ]

        extract_params = {
            "action": "query",
            "pageids": "|".join(page_ids),
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "format": "json"
        }

        extract_response = requests.get(
            BASE_URL,
            params=extract_params,
            headers=HEADERS,
            timeout=15
        )

        extract_response.raise_for_status()

        pages = extract_response.json().get(
            "query", {}
        ).get("pages", {})

        # Step 3: Prepare evidence
        evidence_list = []

        for result in selected_results:

            page_id = str(result["pageid"])

            page = pages.get(page_id, {})

            evidence = page.get("extract", "")

            if not evidence:
                continue

            title = result["title"]

            evidence_list.append({
                "title": title,
                "evidence": clean_text(evidence),
                "source": (
                    "https://en.wikipedia.org/wiki/"
                    + quote(title.replace(" ", "_"))
                )
            })

        return evidence_list

    except requests.RequestException as error:
        print("Evidence retrieval error:", error)
        return []

    except (ValueError, KeyError, TypeError) as error:
        print("Response processing error:", error)
        return []
