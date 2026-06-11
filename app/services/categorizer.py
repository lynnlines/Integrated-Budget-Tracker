import re
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.rule import Rule


class CompiledRule:
    def __init__(self, id, name, pattern, match_type, category_id, priority):
        self.id = id
        self.name = name
        self.pattern = pattern
        self.match_type = match_type
        self.category_id = category_id
        self.priority = priority
        self._regex = re.compile(pattern, flags=re.IGNORECASE) if match_type == "regex" else None

    def matches(self, text: str) -> bool:
        if not text:
            return False
        if self.match_type == "regex":
            return bool(self._regex.search(text))
        # substring default
        return self.pattern.lower() in text.lower()


class RuleEngine:
    def __init__(self, db: Session):
        self.db = db
        self.rules: List[CompiledRule] = []
        self._load_rules()

    def _load_rules(self):
        q = self.db.query(Rule).filter(Rule.enabled == True).order_by(Rule.priority.asc())
        for r in q.all():
            self.rules.append(
                CompiledRule(
                    id=r.id,
                    name=r.name,
                    pattern=r.pattern,
                    match_type=r.match_type,
                    category_id=r.category_id,
                    priority=r.priority,
                )
            )

    def categorize(self, tx: Dict[str, Any]) -> Optional[str]:
        text = (tx.get("description") or "") + " " + (tx.get("raw_payee") or "")
        for r in self.rules:
            if r.matches(text):
                return str(r.category_id)
        return None
