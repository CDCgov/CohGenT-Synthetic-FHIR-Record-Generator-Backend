

import random

from sqlalchemy.orm import Session

from api.database.db_other_tables import Occupation
from api.models.value_types import ValueOccupation


def generate_occupation(occ: ValueOccupation, main_db: Session) -> str:
    specific_occupation_code = occ.occupation_code
    
    if specific_occupation_code is not None:
        occupation = main_db.query(Occupation).filter(
            Occupation.code == specific_occupation_code
        ).first()
        if not occupation:
            raise ValueError(f"Occupation code '{specific_occupation_code}' not found")
        return f"{occupation.system}^{occupation.code}^{occupation.display}"
    else:
        # Random occupation
        total_count = main_db.query(Occupation).count()
        random_offset = random.randint(0, total_count - 1)
        occupation = main_db.query(Occupation).offset(random_offset).limit(1).first()
        if not occupation:
            raise ValueError("Occupation selection failed")
        return f"{occupation.system}^{occupation.code}^{occupation.display}"
