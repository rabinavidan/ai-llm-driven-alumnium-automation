"""
Thin wrappers that put every Alumnium call into an Allure step.

Why: Alumnium expresses intent in natural language. Piping that intent straight
into the Allure report gives you a self-documenting, human-readable test log —
"AI action: add the backpack to the cart", "AI verify: cart shows 1 item" —
without maintaining a parallel set of step descriptions.
"""
import allure


def ai_do(al, instruction: str):
    """Perform a natural-language action."""
    with allure.step(f"🤖 action — {instruction}"):
        return al.do(instruction)


def ai_check(al, assertion: str):
    """Assert a natural-language expectation (raises AssertionError on failure)."""
    with allure.step(f"✅ verify — {assertion}"):
        return al.check(assertion)


def ai_get(al, query: str):
    """Extract a typed value (str/int/float/bool/list) from the current page."""
    with allure.step(f"🔎 extract — {query}"):
        value = al.get(query)
        allure.attach(str(value), name=f"{query} = ", attachment_type=allure.attachment_type.TEXT)
        return value
