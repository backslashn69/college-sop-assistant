import re
from collections import Counter


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "do",
    "does",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "should",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "with",
}


QUERY_EXPANSIONS = {
    "time off": {
        "time",
        "off",
        "leave",
        "vacation",
        "request",
    },
    "leave request": {
        "time",
        "off",
        "leave",
        "vacation",
        "request",
    },
    "sign in": {
        "access",
        "login",
        "credentials",
        "workday",
    },
    "log in": {
        "access",
        "login",
        "credentials",
        "workday",
    },
    "delegation": {
        "delegation",
        "delegate",
        "inbox",
        "supervisor",
    },
    "delegate": {
        "delegation",
        "delegate",
        "inbox",
        "supervisor",
    },
    "get help": {
        "support",
        "help",
        "assistance",
        "hypercare",
        "nexus",
        "service",
        "desk",
    },
    "support": {
        "support",
        "help",
        "assistance",
        "hypercare",
        "nexus",
        "service",
        "desk",
    },
    "mobile app": {
        "mobile",
        "app",
        "organization",
        "njit",
    },
    "banner index": {
        "banner",
        "index",
        "ppgg",
        "program",
        "project",
        "gift",
        "grant",
    },
    "personal information": {
        "personal",
        "profile",
        "address",
        "location",
        "information",
    },
    "physical location": {
        "physical",
        "work",
        "location",
        "manager",
    },
    "physical work location": {
        "physical",
        "work",
        "location",
        "incorrect",
        "manager",
    },
    "training": {
        "training",
        "nexus",
        "knowledge",
        "base",
        "videos",
        "aids",
    },
}


PROCEDURE_WORDS = {
    "access",
    "complete",
    "process",
    "request",
    "set",
    "setup",
    "submit",
    "use",
}


ISSUE_WORDS = {
    "cannot",
    "incorrect",
    "issue",
    "problem",
    "wrong",
}


NUMBERED_STEP_PATTERN = re.compile(
    r"^(\d+)\.\s*(.*)$"
)


def normalize_token(token: str) -> str:
    token = token.lower()

    if len(token) > 4 and token.endswith("ies"):
        return f"{token[:-3]}y"

    if len(token) > 4 and token.endswith("ing"):
        return token[:-3]

    if len(token) > 3 and token.endswith("s"):
        return token[:-1]

    return token


def extract_keywords(text: str) -> list[str]:
    words = re.findall(
        r"[a-z0-9]+",
        text.lower(),
    )

    return [
        normalize_token(word)
        for word in words
        if (
            len(word) > 2
            and word not in STOP_WORDS
        )
    ]


def expand_question_keywords(
    question: str,
) -> set[str]:
    lowered_question = question.lower()

    keywords = set(
        extract_keywords(question)
    )

    for phrase, expansion in QUERY_EXPANSIONS.items():
        if phrase in lowered_question:
            keywords.update(
                normalize_token(word)
                for word in expansion
            )

    return keywords


def normalize_search_text(text: str) -> str:
    """
    Normalize text so important multi-word phrases
    can be compared reliably.
    """
    return " ".join(
        extract_keywords(text)
    )


def extract_question_phrases(
    question: str,
) -> set[str]:
    """
    Build important two-word and three-word phrases
    from the user's question.
    """
    words = extract_keywords(question)

    phrases: set[str] = set()

    for phrase_size in (2, 3):
        for index in range(
            len(words) - phrase_size + 1
        ):
            phrase = " ".join(
                words[
                    index:index + phrase_size
                ]
            )

            phrases.add(phrase)

    return phrases


def score_keyword_overlap(
    question_keywords: set[str],
    text: str,
    weight: int,
) -> int:
    word_counts = Counter(
        extract_keywords(text)
    )

    return sum(
        min(
            word_counts[keyword],
            3,
        )
        * weight
        for keyword in question_keywords
        if word_counts[keyword] > 0
    )


def score_phrase_overlap(
    question_phrases: set[str],
    text: str,
    weight: int,
) -> int:
    normalized_text = normalize_search_text(
        text
    )

    score = 0

    for phrase in question_phrases:
        if phrase in normalized_text:
            score += (
                len(phrase.split())
                * weight
            )

    return score


def is_procedure_question(question: str) -> bool:
    lowered_question = question.strip().lower()

    if lowered_question.startswith("how"):
        return True

    question_keywords = set(
        extract_keywords(question)
    )

    return bool(
        question_keywords
        & PROCEDURE_WORDS
    )


def find_best_sop_chunks(
    question: str,
    sop_chunks: list[
        dict[str, str | int]
    ],
    limit: int = 3,
) -> list[dict[str, str | int]]:
    question_keywords = (
        expand_question_keywords(
            question
        )
    )

    question_phrases = (
        extract_question_phrases(
            question
        )
    )

    if not question_keywords:
        return []

    procedure_question = (
        is_procedure_question(
            question
        )
    )

    scored_chunks: list[
        tuple[
            int,
            dict[str, str | int],
        ]
    ] = []

    for chunk in sop_chunks:
        title = str(
            chunk.get(
                "title",
                "",
            )
        )

        body = str(
            chunk.get(
                "text",
                "",
            )
        )

        section_type = str(
            chunk.get(
                "type",
                "section",
            )
        )

        title_score = (
            score_keyword_overlap(
                question_keywords,
                title,
                weight=12,
            )
        )

        body_score = (
            score_keyword_overlap(
                question_keywords,
                body,
                weight=2,
            )
        )

        title_phrase_score = (
            score_phrase_overlap(
                question_phrases,
                title,
                weight=20,
            )
        )

        body_phrase_score = (
            score_phrase_overlap(
                question_phrases,
                body,
                weight=12,
            )
        )

        total_score = (
            title_score
            + body_score
            + title_phrase_score
            + body_phrase_score
        )

        normalized_question = (
            normalize_search_text(
                question
            )
        )

        normalized_title = (
            normalize_search_text(
                title
            )
        )

        if (
            normalized_question
            and normalized_question
            in normalized_title
        ):
            total_score += 30

        if (
            procedure_question
            and section_type
            == "procedure"
        ):
            total_score += 8

        if (
            procedure_question
            and section_type
            == "reference"
        ):
            total_score -= 12

        if (
            question_keywords
            & ISSUE_WORDS
            and section_type
            == "troubleshooting"
        ):
            total_score += 20

        if total_score > 0:
            scored_chunks.append(
                (
                    total_score,
                    chunk,
                )
            )

    scored_chunks.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    if not scored_chunks:
        return []

    best_score = scored_chunks[0][0]

    minimum_acceptable_score = max(
        6,
        int(best_score * 0.55),
    )

    selected_chunks = [
        chunk
        for score, chunk
        in scored_chunks
        if score
        >= minimum_acceptable_score
    ]

    return selected_chunks[:limit]


def clean_answer_line(line: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        line,
    ).strip()


def normalize_section_lines(
    text: str,
) -> list[str]:
    """
    Remove PDF extraction artifacts and reconnect
    bullet symbols separated from their text.
    """
    raw_lines = [
        clean_answer_line(line)
        for line in text.splitlines()
        if clean_answer_line(line)
    ]

    normalized_lines: list[str] = []
    index = 0

    standalone_bullets = {
        "o",
        "○",
        "-",
        "•",
        "●",
        "▪",
        "◦",
    }

    while index < len(raw_lines):
        line = raw_lines[index]

        if (
            line.lower()
            in standalone_bullets
        ):
            if index + 1 < len(raw_lines):
                next_line = raw_lines[
                    index + 1
                ].strip()

                next_line = re.sub(
                    r"^[•●▪◦-]\s*",
                    "",
                    next_line,
                ).strip()

                if next_line:
                    normalized_lines.append(
                        f"- {next_line}"
                    )

                index += 2
                continue

            index += 1
            continue

        if re.match(
            r"^[•●▪◦-]\s*",
            line,
        ):
            line = re.sub(
                r"^[•●▪◦-]\s*",
                "- ",
                line,
            )

        normalized_lines.append(line)
        index += 1

    return normalized_lines


def clean_subitem(item: str) -> str:
    value = (
        item.removeprefix("- ")
        .strip()
    )

    value = re.sub(
        r",?\s+or$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = (
        value.rstrip(".")
        .strip()
    )

    if value.lower() == "entire inbox":
        return "the entire inbox"

    if value:
        return (
            value[0].lower()
            + value[1:]
        )

    return value

DIRECT_ANSWER_PREFIXES = (
    "what should i do",
    "what do i do",
    "who should",
    "who can",
    "where do",
    "when do",
    "can i",
    "should i",
)


ACTION_KEYWORDS = {
    "ask",
    "contact",
    "correct",
    "notify",
    "review",
    "search",
    "submit",
    "update",
    "use",
    "visit",
    "wait",
}


def is_direct_answer_question(
    question: str,
) -> bool:
    normalized_question = re.sub(
        r"\s+",
        " ",
        question.lower(),
    ).strip()

    return normalized_question.startswith(
        DIRECT_ANSWER_PREFIXES
    )


def build_direct_answer(
    question: str,
    matching_chunks: list[
        dict[str, str | int]
    ],
) -> str | None:
    """
    Select the single SOP instruction that most
    directly answers the user's question.
    """
    question_keywords = (
        expand_question_keywords(
            question
        )
    )

    question_phrases = (
        extract_question_phrases(
            question
        )
    )

    ranked_lines: list[
        tuple[
            int,
            int,
            int,
            str,
        ]
    ] = []

    for chunk_index, chunk in enumerate(
        matching_chunks
    ):
        lines = normalize_section_lines(
            str(
                chunk.get(
                    "text",
                    "",
                )
            )
        )

        for line_index, line in enumerate(
            lines
        ):
            cleaned_line = re.sub(
                r"^\d+\.\s*",
                "",
                line,
            ).strip()

            cleaned_line = (
                cleaned_line
                .removeprefix("- ")
                .strip()
            )

            if (
                len(cleaned_line.split()) < 5
                or cleaned_line.lower()
                in {
                    "important",
                    "employees should",
                    "examples include",
                }
            ):
                continue

            line_score = (
                score_keyword_overlap(
                    question_keywords,
                    cleaned_line,
                    weight=6,
                )
            )

            line_score += (
                score_phrase_overlap(
                    question_phrases,
                    cleaned_line,
                    weight=18,
                )
            )

            line_keywords = set(
                extract_keywords(
                    cleaned_line
                )
            )

            if (
                line_keywords
                & ACTION_KEYWORDS
            ):
                line_score += 10

            if line_score > 0:
                ranked_lines.append(
                    (
                        line_score,
                        chunk_index,
                        line_index,
                        cleaned_line,
                    )
                )

    if not ranked_lines:
        return None

    ranked_lines.sort(
        key=lambda item: (
            item[0],
            -item[1],
            -len(item[3]),
        ),
        reverse=True,
    )

    answer = ranked_lines[0][3]

    answer = re.sub(
        r"^(Ask|Notify|Contact) "
        r"the manager\b",
        r"\1 your manager",
        answer,
        flags=re.IGNORECASE,
    )

    answer = re.sub(
        r"\bthe physical work location\b",
        "your physical work location",
        answer,
        flags=re.IGNORECASE,
    )

    if not answer.endswith(
        (
            ".",
            "!",
            "?",
        )
    ):
        answer += "."

    return answer

def format_procedure_answer(
    title: str,
    text: str,
) -> str | None:
    lines = normalize_section_lines(
        text
    )

    if not lines:
        return None

    procedure_name = re.sub(
        r"^Step\s+\d+\s*:\s*",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    steps: list[
        tuple[
            int,
            str,
            list[str],
        ]
    ] = []

    important_lines: list[str] = []

    current_number: int | None = None
    current_text = ""
    current_subitems: list[str] = []
    reading_important = False

    def save_current_step() -> None:
        nonlocal current_number
        nonlocal current_text
        nonlocal current_subitems

        if current_number is None:
            return

        step_text = current_text.strip()

        if current_subitems:
            cleaned_items = [
                clean_subitem(item)
                for item
                in current_subitems
                if clean_subitem(item)
            ]

            if (
                step_text
                .rstrip(":")
                .lower()
                == "select"
            ):
                step_text = (
                    "Select either "
                    + " or ".join(
                        cleaned_items
                    )
                )

            else:
                step_text = (
                    step_text.rstrip(":")
                    + ": "
                    + "; ".join(
                        cleaned_items
                    )
                )

        if (
            step_text
            and not step_text.endswith(
                (
                    ".",
                    "!",
                    "?",
                )
            )
        ):
            step_text += "."

        steps.append(
            (
                current_number,
                step_text,
                current_subitems.copy(),
            )
        )

        current_number = None
        current_text = ""
        current_subitems = []

    for line in lines:
        if (
            line.lower()
            == "important"
        ):
            save_current_step()
            reading_important = True
            continue

        if reading_important:
            important_lines.append(
                line
            )
            continue

        step_match = (
            NUMBERED_STEP_PATTERN.match(
                line
            )
        )

        if step_match:
            save_current_step()

            current_number = int(
                step_match.group(1)
            )

            current_text = (
                step_match
                .group(2)
                .strip()
            )

            continue

        if (
            current_number is not None
            and line.startswith("- ")
        ):
            current_subitems.append(
                line
            )
            continue

        if current_number is not None:
            current_text = (
                f"{current_text} {line}"
            ).strip()

    save_current_step()

    heading = (
        f"To "
        f"{procedure_name[:1].lower()}"
        f"{procedure_name[1:]}:"
    )

    if not steps:
        answer_lines = [
            heading,
            "",
        ]

        for line in lines:
            cleaned_line = line.strip()

            if not cleaned_line:
                continue

            if (
                cleaned_line.lower()
                == "important"
            ):
                answer_lines.extend(
                    [
                        "",
                        "Important:",
                    ]
                )
                continue

            is_short_heading = (
                len(cleaned_line) < 60
                and not cleaned_line
                .startswith("- ")
                and not cleaned_line
                .endswith(
                    (
                        ".",
                        ":",
                        "!",
                        "?",
                    )
                )
            )

            if is_short_heading:
                if (
                    answer_lines
                    and answer_lines[-1]
                    != ""
                ):
                    answer_lines.append("")

                cleaned_line = (
                    f"{cleaned_line}:"
                )

            answer_lines.append(
                cleaned_line
            )

        return "\n".join(
            answer_lines
        ).strip()

    answer_lines = [
        heading,
        "",
    ]

    for (
        number,
        step_text,
        _,
    ) in steps:
        answer_lines.append(
            f"{number}. {step_text}"
        )

    if important_lines:
        warning = " ".join(
            important_lines
        ).strip()

        answer_lines.extend(
            [
                "",
                f"Important: {warning}",
            ]
        )

    return "\n".join(
        answer_lines
    ).strip()


def build_precise_answer(
    question: str,
    matching_chunks: list[
        dict[str, str | int]
    ],
) -> str | None:
    if not matching_chunks:
        return None

    primary_chunk = matching_chunks[0]

    title = str(
        primary_chunk.get(
            "title",
            "Relevant SOP section",
        )
    ).strip()

    body_lines = [
        clean_answer_line(line)
        for line in str(
            primary_chunk["text"]
        ).splitlines()
        if clean_answer_line(line)
    ]

    if not body_lines:
        return None

    question_keywords = (
        expand_question_keywords(
            question
        )
    )

    question_phrases = (
        extract_question_phrases(
            question
        )
    )

    title_keywords = set(
        extract_keywords(title)
    )

    title_match_count = len(
        question_keywords
        & title_keywords
    )

    section_type = str(
        primary_chunk.get(
            "type",
            "section",
        )
    )

    return_complete_section = (
        section_type == "procedure"
        and title_match_count > 0
    )

    if return_complete_section:
        return format_procedure_answer(
            title,
            str(
                primary_chunk["text"]
            ),
        )

    if is_direct_answer_question(
        question
    ):
        direct_answer = (
            build_direct_answer(
                question,
                matching_chunks,
            )
        )

        if direct_answer:
            return direct_answer

    ranked_lines: list[
        tuple[
            int,
            int,
            str,
        ]
    ] = []

    for index, line in enumerate(
        body_lines
    ):
        line_score = (
            score_keyword_overlap(
                question_keywords,
                line,
                weight=4,
            )
        )

        line_score += (
            score_phrase_overlap(
                question_phrases,
                line,
                weight=14,
            )
        )

        if line_score > 0:
            ranked_lines.append(
                (
                    line_score,
                    index,
                    line,
                )
            )

    if not ranked_lines:
        return None

    ranked_lines.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    selected_indices: set[int] = set()

    for (
        _,
        index,
        _,
    ) in ranked_lines[:3]:
        selected_indices.add(index)

        if index > 0:
            previous_line = body_lines[
                index - 1
            ]

            if (
                len(previous_line) < 70
                and not previous_line
                .startswith("- ")
            ):
                selected_indices.add(
                    index - 1
                )

        if (
            index + 1
            < len(body_lines)
        ):
            next_line = body_lines[
                index + 1
            ]

            if next_line.startswith("- "):
                selected_indices.add(
                    index + 1
                )

    selected_lines = [
        body_lines[index]
        for index in sorted(
            selected_indices
        )
        if body_lines[index]
        not in {
            "-",
            "o",
            "○",
        }
    ]

    if not selected_lines:
        return None

    return "\n".join(
        selected_lines
    ).strip()