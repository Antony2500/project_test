from pydantic import BaseModel, validator, ValidationError


list_14 = [13, "Faf", False, True, "fafaf"]

for i, v in enumerate(list_14):
    print(i, v)