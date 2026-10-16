from pydantic import ValidationError
from app.schemas import TaskCreate

test_names = [
    "Build AI agent",
    "",
    "  ",
    "  Python  ",
    "A" * 201
]

for name in test_names:
    try:
        task = TaskCreate(name=name)
        print(f"VALID: '{repr(task.name)}'")
    except ValidationError :
        print(f"INVALID: '{repr(name)}'")