from typing import Dict
from uuid import UUID
from datetime import datetime
from sentence_transformers import SentenceTransformer
from dateutil.relativedelta import relativedelta

from models.candidate_model import CandidateModel

from utils.prompt import TEXT_CANDIDATE


class CandidateService:
    def __init__(self, database, model: SentenceTransformer):
        self.database = database
        self.model = model

    def calculate_tenure(self, experiences: list) -> int:
        """Calculate total working experience in years."""
        total_months = 0
        for exp in experiences:
            start_date = datetime.strptime(exp["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(exp["end_date"], "%Y-%m-%d")
            diff = relativedelta(end_date, start_date)
            total_months += diff.years * 12 + diff.months

        return total_months // 12

    def create_candidate_text(self, candidate_data: Dict) -> str:
        """Create formatted candidate text for embedding."""
        current_exp = candidate_data["experiences"][-1]
        previous_exp = (
            candidate_data["experiences"][-2]
            if len(candidate_data["experiences"]) > 1
            else None
        )

        education = []
        for edu in candidate_data["education"]:
            education.append(f"{edu['degree']} from {edu['institution']}")

        candidate_text = TEXT_CANDIDATE.format(
            years=self.calculate_tenure(candidate_data["experiences"]),
            current_role=current_exp["role"],
            current_company=current_exp["company"],
            previous_role=previous_exp["role"] if previous_exp else "None",
            skills=", ".join(candidate_data["skills"]),
            education=", ".join(education),
        )
        return candidate_text

    def create_candidate_model(
        self,
        candidate_id: UUID,
        candidate_data: Dict,
        candidate_embedding: list,
        status: str = "active",
    ) -> CandidateModel:
        """Create Candidate instance from data."""
        # Get experiences
        current_exp = candidate_data["experiences"][-1]
        previous_exp = (
            candidate_data["experiences"][-2]
            if len(candidate_data["experiences"]) > 1
            else None
        )

        # Get education
        bachelor_edu = None
        master_edu = None
        for edu in candidate_data["education"]:
            if "B.Sc." in edu["degree"]:
                bachelor_edu = edu
            elif "M.Sc." in edu["degree"]:
                master_edu = edu

        return CandidateModel(
            candidate_id=candidate_id,
            first_name=candidate_data["first_name"],
            last_name=candidate_data["last_name"],
            birthdate=candidate_data["birthdate"],
            email=candidate_data["email"],
            phone=candidate_data["phone"],
            address=candidate_data["address"],
            skills=", ".join(candidate_data["skills"]),
            current_company=current_exp["company"],
            current_job_role=current_exp["role"],
            current_start_date=current_exp["start_date"],
            current_end_date=current_exp["end_date"],
            previous_company=previous_exp["company"] if previous_exp else None,
            previous_job_role=previous_exp["role"] if previous_exp else None,
            previous_start_date=(
                previous_exp["start_date"] if previous_exp else None
            ),
            previous_end_date=(
                previous_exp["end_date"] if previous_exp else None
            ),
            # Education
            bachelor_institution=(
                bachelor_edu["institution"] if bachelor_edu else None
            ),
            bachelor_degree=bachelor_edu["degree"] if bachelor_edu else None,
            bachelor_graduation_year=(
                bachelor_edu["year_of_graduation"] if bachelor_edu else None
            ),
            has_bachelor=bool(bachelor_edu),
            master_institution=(
                master_edu["institution"] if master_edu else None
            ),
            master_degree=master_edu["degree"] if master_edu else None,
            master_graduation_year=(
                master_edu["year_of_graduation"] if master_edu else None
            ),
            has_master=bool(master_edu),
            candidate_tenure=self.calculate_tenure(
                candidate_data["experiences"]
            ),
            candidate_embedding=candidate_embedding,
        )

    def process_candidate(
        self, candidate_id: UUID, candidate_data: Dict
    ) -> bool:
        """Process and insert new candidate data to database."""
        try:
            # Create text for embedding
            candidate_text = self.create_candidate_text(candidate_data)

            # Generate embedding
            candidate_embedding = self.model.encode(
                candidate_text, task="separation", truncate_dim=32
            )

            # Create candidate model
            candidate_model = self.create_candidate_model(
                candidate_id=candidate_id,
                candidate_data=candidate_data,
                candidate_embedding=candidate_embedding,
            )

            # Store in database
            with self.database.get_session() as session:
                session.add(candidate_model)
                session.commit()
            return True

        except Exception as e:
            print(f"Error processing candidate: {str(e)}")
            return False

    def update_candidate(
        self, candidate_id: UUID, update_candidate_data: Dict
    ) -> bool:
        """Update existing candidate.

        Args:
            candidate_id: ID of candidate to update
            candidate_data: New candidate information

        Returns:
            bool indicating success/failure
        """

        try:
            with self.database.get_session() as session:
                # Check if candidate exists
                existing_candidate = (
                    session.query(CandidateModel)
                    .filter(CandidateModel.candidate_id == candidate_id)
                    .first()
                )

                if not existing_candidate:
                    raise ValueError(
                        f"No candidate found with ID: {candidate_id}"
                    )

                # Convert to dict and update with new data
                candidate_data = existing_candidate.__dict__
                candidate_data.pop("_sa_instance_state", None)

                # Update provided fields
                for field, value in update_candidate_data.items():
                    if value is not None:
                        candidate_data[field] = value

                # Process updated data
                return self.process_candidate(
                    candidate_id=candidate_id, candidate_data=candidate_data
                )

        except Exception as e:
            print(f"Error updating candidate: {str(e)}")
            return False
