from __future__ import annotations # This import allows for postponed evaluation of type annotations, which can help with forward references and circular imports.

from textwrap import dedent # This import is used to remove any common leading whitespace from every line in a given text. It's often used to format multi-line strings in a more readable way in the code without affecting the actual string content.
from typing import Final # This import is used to indicate that a variable is intended to be a constant and should not be reassigned. It serves as a hint to developers and type checkers that the value should not change after it's set.

SCHEMA_DESCRIPTION = dedent(
    """
    Schema:
    - Users(id, name, join_date)
    - Sales(id, user_id, amount, date)

    Relationship:
    - Sales.user_id = Users.id
    """
).strip()

SYSTEM_PROMPT = dedent(
    f"""
    You are an expert SQL generator.

    Your task is to convert a user's natural language request into a valid SQL query for the following database schema only:

    {SCHEMA_DESCRIPTION}

    Rules:
    - Only use the tables and columns listed above.
    - Do not invent tables, columns, or relationships.
    - Generate only a SQL query, with no explanation unless the user explicitly asks for one.
    - Prefer clear, correct, readable SQL.
    - If the request is ambiguous, make the safest reasonable assumption based on the schema.
    - If the request cannot be answered from this schema, reply exactly with:
      CANNOT_ANSWER_FROM_SCHEMA
    """
).strip()

VAGUE_SYSTEM_PROMPT: Final[str] = dedent(
        f"""
        You write SQL queries for this schema only:

        {SCHEMA_DESCRIPTION}

        Return only SQL.
        """
).strip()

FEW_SHOT_SYSTEM_PROMPT: Final[str] = SYSTEM_PROMPT

REASONING_SYSTEM_PROMPT: Final[str] = dedent(
        f"""
        You are an expert SQL generator.

        Your task is to convert a user's natural language request into a valid SQL query for the following database schema only:

        {SCHEMA_DESCRIPTION}

        Rules:
        - Only use the tables and columns listed above.
        - Do not invent tables, columns, or relationships.
        - Reason step by step internally before answering.
        - First identify the required table or tables.
        - Then identify the join key when more than one table is required.
        - Then determine filters, grouping, aggregation, and ordering.
        - Do not reveal your reasoning.
        - Return only the final SQL query unless the user explicitly asks for explanation.
        - If the request cannot be answered from this schema, reply exactly with:
            CANNOT_ANSWER_FROM_SCHEMA
        """
).strip()

EXAMPLES = [
    {
        "request": "Show all users",
        "sql": "SELECT id, name, join_date FROM Users;",
    },
    {
        "request": "Find total sales for each user",
        "sql": (
            "SELECT Users.id, Users.name, SUM(Sales.amount) AS total_sales\n"
            "FROM Users\n"
            "JOIN Sales ON Sales.user_id = Users.id\n"
            "GROUP BY Users.id, Users.name;"
        ),
    },
    {
        "request": "Show sales made after 2024-01-01",
        "sql": (
            "SELECT id, user_id, amount, date\n"
            "FROM Sales\n"
            "WHERE date > '2024-01-01';"
        ),
    },
    {
        "request": "List users who have made at least one sale",
        "sql": (
            "SELECT DISTINCT Users.id, Users.name, Users.join_date\n"
            "FROM Users\n"
            "JOIN Sales ON Sales.user_id = Users.id;"
        ),
    },
]

FEW_SHOT_EXAMPLES: Final[list[dict[str, str]]] = EXAMPLES[:2]

PROMPT_DRAFTS: Final[dict[str, dict[str, str]]] = {
    'draft_1': {
        'label': 'Draft 1: Vague',
        'summary': 'Minimal schema prompt. More likely to fail on vague user requests.',
    },
    'draft_2': {
        'label': 'Draft 2: Few-shot',
        'summary': 'Schema plus two examples to anchor output format and joins.',
    },
    'draft_3': {
        'label': 'Draft 3: Structured reasoning',
        'summary': 'Instructs the model to reason internally about joins, sums, and ordering before returning SQL.',
    },
}

INPUT_REFERENCE_EXAMPLES: Final[list[dict[str, str]]] = [
    {
        'title': 'Basic list',
        'input': 'Show all users',
        'note': 'Useful for verifying simple single-table queries.',
    },
    {
        'title': 'Aggregation',
        'input': 'Find total sales for each user',
        'note': 'Tests join plus SUM and GROUP BY.',
    },
    {
        'title': 'Filter by date',
        'input': 'Show sales made after 2024-01-01',
        'note': 'Tests filtering on the Sales table.',
    },
    {
        'title': 'Existence query',
        'input': 'List users who have made at least one sale',
        'note': 'Tests join logic without aggregation.',
    },
    {
        'title': 'Top users experiment',
        'input': 'Give me a query to find top users',
        'note': 'Good for comparing Draft 1, Draft 2, and Draft 3 behavior.',
    },
]


def build_user_prompt(natural_language_request: str) -> str:  
    request = natural_language_request.strip()
    return dedent(
        f"""
        Convert this request into SQL for the given schema.

        Request:
        {request}

        Return only the SQL query.
        """
    ).strip()


def build_examples_text(examples: list[dict[str, str]]) -> str:
    examples_text = []
    for example in examples:
        examples_text.append(f"User: {example['request']}\nSQL: {example['sql']}")
    return "\n\n".join(examples_text)


def build_few_shot_prompt() -> str:
    return build_examples_text(EXAMPLES)


def get_prompt_draft(draft_key: str) -> dict[str, str]:
    return PROMPT_DRAFTS.get(draft_key, PROMPT_DRAFTS['draft_2'])


def build_system_prompt_for_draft(draft_key: str) -> str:
    if draft_key == 'draft_1':
        return VAGUE_SYSTEM_PROMPT
    if draft_key == 'draft_3':
        return REASONING_SYSTEM_PROMPT
    return FEW_SHOT_SYSTEM_PROMPT


def build_examples_for_draft(draft_key: str) -> str:
    if draft_key == 'draft_2':
        return build_examples_text(FEW_SHOT_EXAMPLES)
    return ''


def build_playground_prompt(natural_language_request: str, draft_key: str = 'draft_2') -> str:
    system_prompt = build_system_prompt_for_draft(draft_key)
    examples_text = build_examples_for_draft(draft_key)
    user_prompt = build_user_prompt(natural_language_request)

    prompt_sections = [
        f"System Prompt:\n{system_prompt}",
    ]
    if examples_text:
        prompt_sections.append(f"Examples:\n{examples_text}")
    prompt_sections.append(f"User Prompt:\n{user_prompt}")
    return "\n\n".join(prompt_sections).strip()