"""One-shot claim extraction: feeds a full transcript to Claude in a single
request and writes each claim as a (quote, explanation) row to CSV.
"""

import csv
import sys
from pathlib import Path
from typing import List

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

MODEL = "claude-opus-5"

TRANSCRIPT_PATH = Path(__file__).parent / "cappuccino_index_transcript.txt"
OUTPUT_CSV_PATH = Path(__file__).parent / "claims_comparisons.csv"

load_dotenv(Path(__file__).parent.parent / ".env")


class Claim(BaseModel):
    quote: str
    explanation: str


class ClaimsList(BaseModel):
    claims: List[Claim]


PROMPT_TEMPLATE = """Below is the full transcript of a video. Read the entire \
thing and extract only the speaker's COMPARATIVE claims — that is, claims that \
either:

(a) explicitly compare two or more countries/cities/places to each other (e.g. \
"Ireland is faster than the UK", "Switzerland's cappuccino edges out Denmark's"), \
or
(b) compare a single country/place to the group as a whole — an average, a \
correlation with another index (GDP, cost of living), or a change over time \
relative to the broader trend (e.g. "the index went up in Denmark, Norway, Spain \
and Japan, unlike most of the world", "it correlates well with GDP").

Do NOT include claims that state a single fact about one country/place in \
isolation with no comparison (e.g. a bare "Australia's index is 10:05" with \
nothing compared against it) — skip those entirely, even if they were \
interesting facts.

For each comparative claim, give:

- quote: the exact wording from the transcript stating the claim, trimmed down to \
just the clause(s) carrying the comparison — cut lead-in banter, filler ("well", \
"now", "a little bit of a surprise"), and asides. Keep it a single short sentence \
or fragment, verbatim from the transcript (no paraphrasing).
- explanation: a concise phrase (under 12 words) stating what is being compared \
to what, and the result — not a restatement of the quote, just the key takeaway.

Favor more, shorter claims over fewer, longer ones — split compound comparisons \
into separate rows.

Transcript:
<transcript>
{transcript}
</transcript>"""


def main() -> None:
    if not TRANSCRIPT_PATH.exists():
        sys.exit(f"Transcript not found: {TRANSCRIPT_PATH}")

    transcript = TRANSCRIPT_PATH.read_text(encoding="utf-8")

    client = anthropic.Anthropic()

    response = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(transcript=transcript),
            }
        ],
        output_format=ClaimsList,
    )

    claims = response.parsed_output.claims

    with OUTPUT_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["quote", "explanation"])
        for claim in claims:
            writer.writerow([claim.quote, claim.explanation])

    print(f"Wrote {len(claims)} claims to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
