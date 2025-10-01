from app import models
from datetime import datetime

def test_create_expense_and_tags(db, test_user):
    tag1 = models.Tag(name="food", user_id=test_user.id)
    tag2 = models.Tag(name="work", user_id=test_user.id)
    expense = models.Expense(
        title="Lunch",
        amount=12.5,
        type="expense",
        timestamp=datetime(2025, 9, 20),
        user_id=test_user.id,
        tags=[tag1, tag2]
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    assert expense.id is not None
    assert expense.title == "Lunch"
    assert len(expense.tags) == 2
    assert tag1 in expense.tags
    assert tag2 in expense.tags
