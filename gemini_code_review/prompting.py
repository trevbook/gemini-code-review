"""
Module that handles prompting the Gemini API.
"""

# =====
# SETUP
# =====

from dotenv import load_dotenv

load_dotenv(override=True)

import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic import BaseModel, Field


# Configure model provider
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")
provider = GoogleProvider(api_key=google_api_key)
model = GoogleModel(model_name="gemini-2.5-pro", provider=provider)


def generate_system_prompt(
    n_issues_to_surface: int = 10, user_instructions: Optional[str] = None
) -> str:
    """Generate the system prompt for the code review agent."""

    prompt_template = f"""# Role
You are a code review assistant, tasked with analyzing an entire codebase and providing detailed feedback on potential issues, improvements, and best practices.

# Task
The user will provide you with an XML representation of their codebase.

You'll identify {n_issues_to_surface} of the most impactful, actionable issues that could be addressed to help improve the codebase.

# Issue Types
These issues could include, but are not limited to:

- **Architecture**: Problems in overall system design, layering, modularity, or dependency management that make the code harder to scale or adapt.
- **Documentation (docs)**: Missing or unclear README, inline comments, or API usage guides that make it difficult for new developers to understand and use the code.
- **Security**: Vulnerable patterns (e.g. hardcoded secrets, unsafe dependencies, missing input validation) that could expose the system to risk.
- **Efficiency (performance)**: Inefficient algorithms, repeated computations, or resource-heavy operations that hurt runtime performance or cost.
- **Readability (maintainability)**: Inconsistent naming, formatting, or style that makes the code confusing and prone to errors.
- **Testing**: Gaps in automated test coverage, flaky tests, or missing integration/CI checks that weaken confidence in changes.
- **Developer experience (devx)**: Build process, environment setup, or tooling issues (e.g. missing linters, unclear contribution guidelines) that slow down development.

[USER_INSTRUCTIONS]

# Output Format
You'll respond with a well-structured JSON object matching the provided schema. For each issue, also include an `implementation_plan` of 1-3 sentences describing concrete next steps to address the issue.
"""

    if user_instructions:
        user_instructions_clause = f"""# User Instructions
The user provided some additional instructions to consider while performing the code review:

---

{user_instructions}

---
"""
        prompt_template = prompt_template.replace("[USER_INSTRUCTIONS]", user_instructions_clause)
    else:
        prompt_template = prompt_template.replace("[USER_INSTRUCTIONS]", "")

    return prompt_template


class CodebaseIssue(BaseModel):
    """Schema for a single codebase issue identified by the agent."""

    category: str = Field(
        ..., description='Issue category (e.g., "Architecture", "Docs", "Security", "Efficiency", "Readability", "Testing", "DevX").'
    )
    title: str = Field(..., description="Concise one-line name for the issue (~8 words).")
    rationale: str = Field(..., description="Short explanation of why this issue matters.")
    detailed_description: str = Field(
        ..., description="Detailed description, including specific examples from the codebase if possible."
    )
    severity: str = Field(..., description="One of: 'Low', 'Medium', 'High', 'Critical'.")
    location: str = Field(
        ..., description="Where the issue occurs (file, directory, class, function, etc.)."
    )
    estimated_effort: str = Field(
        ..., description="One of: 'Low' (minutes), 'Medium' (hours), 'High' (days), 'Very High' (weeks+)."
    )
    implementation_plan: str = Field(
        ..., description="1-3 sentences describing how to approach fixing the issue."
    )


class CodeReviewResponse(BaseModel):
    """Schema for the overall response from the code review agent."""

    issues: list[CodebaseIssue] = Field(..., description="List of identified issues.")


def run_code_review(
    codebase_xml: str,
    n_issues_to_surface: int = 10,
    user_instructions: Optional[str] = None,
) -> CodeReviewResponse:
    """Run the Gemini Code Review agent on the provided codebase XML."""

    system_prompt = generate_system_prompt(
        n_issues_to_surface=n_issues_to_surface, user_instructions=user_instructions
    )

    agent = Agent(model=model, system_prompt=system_prompt, output_type=CodeReviewResponse)
    result = agent.run_sync(codebase_xml)
    return result.output


