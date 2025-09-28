from app import models

def test_create_expense_and_tags(db):
    tag1 = models.Tag(name="food")
    tag2 = models.Tag(name="work")
    expense = models.Expense(title="Lunch", amount=12.5, type="expense", tags=[tag1, tag2])

    db.add(expense)
    db.commit()
    db.refresh(expense)

    assert expense.id is not None
    assert expense.title == "Lunch"
    assert len(expense.tags) == 2
    assert tag1 in expense.tags
    assert tag2 in expense.tags
