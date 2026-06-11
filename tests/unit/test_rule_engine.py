from app.services.categorizer import CompiledRule, RuleEngine


def test_compiled_rule_matches_substring():
    r = CompiledRule(id="1", name="r1", pattern="STARBUCKS", match_type="substring", category_id="c1", priority=10)
    assert r.matches("Starbucks downtown")
    assert not r.matches("")


def test_ruleengine_categorize():
    engine = object.__new__(RuleEngine)
    engine.db = None
    engine.rules = [
        CompiledRule(id="1", name="r1", pattern="STARBUCKS", match_type="substring", category_id="coffee", priority=10),
        CompiledRule(id="2", name="r2", pattern=r"\bNETFLIX\b", match_type="regex", category_id="entertainment", priority=20),
    ]

    tx1 = {"description": "STARBUCKS 123", "raw_payee": ""}
    assert engine.categorize(tx1) == "coffee"

    tx2 = {"description": "monthly NETFLIX subscription", "raw_payee": ""}
    assert engine.categorize(tx2) == "entertainment"

    tx3 = {"description": "unknown merchant", "raw_payee": ""}
    assert engine.categorize(tx3) is None
