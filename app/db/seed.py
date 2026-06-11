from uuid import uuid4
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.rule import Rule


def seed_rules_and_categories():
    categories = [
        {"name": "Coffee"},
        {"name": "Gas"},
        {"name": "Entertainment"},
        {"name": "Groceries"},
        {"name": "Income"},
    ]

    rules = [
        {"name": "Starbucks", "pattern": "STARBUCKS", "match_type": "substring", "category_name": "Coffee", "priority": 10},
        {"name": "Shell", "pattern": "SHELL", "match_type": "substring", "category_name": "Gas", "priority": 20},
        {"name": "Netflix", "pattern": "NETFLIX", "match_type": "substring", "category_name": "Entertainment", "priority": 30},
        {"name": "Whole Foods", "pattern": "WHOLE FOODS", "match_type": "substring", "category_name": "Groceries", "priority": 40},
    ]

    with SessionLocal() as db:
        existing = {c.name: c for c in db.query(Category).all()}
        for category in categories:
            if category["name"] not in existing:
                new_category = Category(id=uuid4(), name=category["name"])
                db.add(new_category)
                existing[category["name"]] = new_category

        db.commit()

        for rule in rules:
            category = existing.get(rule["category_name"])
            if category is None:
                continue
            exists = db.query(Rule).filter(Rule.name == rule["name"]).one_or_none()
            if not exists:
                db.add(
                    Rule(
                        id=uuid4(),
                        name=rule["name"],
                        pattern=rule["pattern"],
                        match_type=rule["match_type"],
                        category_id=category.id,
                        priority=rule["priority"],
                    )
                )
        db.commit()


if __name__ == "__main__":
    seed_rules_and_categories()
    print("Seeded categories and rules.")
