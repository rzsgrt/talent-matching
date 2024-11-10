from json.decoder import JSONDecodeError
from typing import Dict, Optional
from uuid import UUID

import ollama
from sentence_transformers import SentenceTransformer

from models.job_model import JobModel
from utils.prompt import (
    ADDITIONAL_EDUCATION_TEXT_JOB,
    ADDITIONAL_TENURE_TEXT_JOB,
    PROMPT_JOB_DESCRIPTION,
    TEXT_JOB,
)


class JobService:
    def __init__(self, database, model: SentenceTransformer):
        self.database = database
        self.model = model

    def extract_job_description(self, job_description: str) -> Dict:
        """Extract structured information from job description using LLM."""
        try:
            response = ollama.generate(
                model="llama3.2:1b",
                prompt=PROMPT_JOB_DESCRIPTION.format(
                    job_description=job_description
                ),
            )
            return response["response"]
        except Exception as e:
            raise JSONDecodeError(
                f"Failed to parse job description: {str(e)}", "", 0
            )

    def create_job_text(self, job_data: Dict, job_desc_info: Dict) -> str:
        """Create formatted job text for embedding."""
        job_text = TEXT_JOB.format(
            role=job_data["job_title"],
            description=job_data["job_description"],
            required_skills=", ".join(job_data["required_skills"]),
        )

        if job_desc_info["tenure"] != 0:
            job_text += ADDITIONAL_TENURE_TEXT_JOB.format(
                tenure=job_desc_info["tenure"]
            )

        if (
            job_desc_info["is_required_master"]
            or job_desc_info["is_required_bachelor"]
        ):
            education = " ".join(
                [
                    ", ".join(job_desc_info["bachelor_program"]),
                    ", ".join(job_desc_info["master_program"]),
                ]
            )
            job_text += ADDITIONAL_EDUCATION_TEXT_JOB.format(
                education=education
            )

        return job_text

    def create_job_model(
        self,
        job_id: UUID,
        job_data: Dict,
        job_desc_info: Dict,
        job_embedding: list,
        previous_version_id: Optional[UUID] = None,
        status: str = "active",
    ) -> JobModel:
        """Create JobModel instance from job data."""
        return JobModel(
            job_id=job_id,
            job_title=job_data["job_title"],
            job_description=job_data["job_description"],
            budget_min=job_data["budget"]["min"],
            budget_max=job_data["budget"]["max"],
            budget_currency=job_data["budget"]["currency"],
            location=job_data["location"],
            company_name=job_data["company_name"],
            employment_type=job_data["employment_type"],
            required_skills=", ".join(job_data["required_skills"]),
            is_bachelor=job_desc_info["is_required_bachelor"],
            is_master=job_desc_info["is_required_master"],
            bachelor_program=", ".join(job_desc_info["bachelor_program"]),
            master_program=", ".join(job_desc_info["master_program"]),
            tenure=job_desc_info["tenure"],
            job_embedding=job_embedding,
            previous_version_id=previous_version_id,
            status=status,
        )

    def get_embedding(self, job_text: str, task="separation", size=32):
        """Get embedding from embedding model."""
        job_embedding = self.model.encode(
            job_text, task=task, truncate_dim=size
        )
        return job_embedding

    def process_job(
        self,
        job_id: UUID,
        job_data: Dict,
        previous_version_id: Optional[UUID] = None,
    ) -> bool:
        """Process job data and store in database."""
        try:
            # Process job information
            job_desc_info = self.extract_job_description(
                job_data["job_description"]
            )
            job_text = self.create_job_text(job_data, job_desc_info)
            job_embedding = self.get_embedding(job_text)

            # Create and store job model
            job_model = self.create_job_model(
                job_id=job_id,
                job_data=job_data,
                job_desc_info=job_desc_info,
                job_embedding=job_embedding,
                previous_version_id=previous_version_id,
            )

            with self.database.get_session() as session:
                session.add(job_model)
                session.commit()

            return True

        except Exception as e:
            print(f"Error processing job: {str(e)}")
            return False

    def update_job(
        self, new_job_id: UUID, previous_job_id: UUID, job_data: Dict
    ) -> bool:
        """Update existing job by creating new version and marking old as inactive."""
        try:
            with self.database.get_session() as session:
                # Get and validate existing job
                existing_job = (
                    session.query(JobModel)
                    .filter(
                        JobModel.job_id == previous_job_id,
                        JobModel.status == "active",
                    )
                    .first()
                )

                if not existing_job:
                    raise ValueError(
                        f"No active job found with ID: {previous_job_id}"
                    )

                # Update status and create new version
                existing_job.status = "inactive"
                session.commit()

                return self.process_job(
                    job_id=new_job_id,
                    job_data=job_data,
                    previous_version_id=previous_job_id,
                )

        except Exception as e:
            print(f"Error updating job: {str(e)}")
            return False
