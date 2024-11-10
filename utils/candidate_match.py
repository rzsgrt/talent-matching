from typing import List, Dict
from uuid import UUID
from sqlalchemy import text
from models.job_model import JobModel


class CandidateMatch:
    def __init__(self, database):
        self.database = database

    def get_candidates_by_job(
        self, job_id: UUID, total_candidate: int
    ) -> List[Dict]:
        """Get matching candidates for a job.

        Args:
            job_id: UUID of the job

        Returns:
            List of candidates with similarity scores
        """
        try:
            with self.database.get_session() as session:
                # Get job
                job = (
                    session.query(JobModel)
                    .filter(
                        JobModel.job_id == job_id, JobModel.status == "active"
                    )
                    .first()
                )

                if not job:
                    raise ValueError(f"No active job found with ID: {job_id}")

                # Get candidates filtered by tenure
                query = text(
                    """
                    WITH similarity_scores AS (
                        SELECT
                            candidate_id,
                            first_name,
                            last_name,
                            email,
                            1 - (job_embedding <#> candidate_embedding) as similarity_score
                        FROM
                            candidates c
                        WHERE
                            c.candidate_tenure >= :min_tenure AND
                            CASE WHEN :req_bachelor THEN c.has_bachelor = true ELSE true END AND
                            CASE WHEN :req_master THEN c.has_master = true ELSE true END
                        ORDER BY
                            similarity_score DESC
                        LIMIT :total_candidate
                    )
                    SELECT * FROM similarity_scores;
                    """
                )

                result = session.execute(
                    query,
                    {
                        "min_tenure": job.tenure if job.tenure else 0,
                        "req_bachelor": True if job.is_bachelor else False,
                        "req_master": True if job.is_master else False,
                        "total_candidate": total_candidate,
                    },
                )

                candidates = []
                for row in result:
                    candidates.append(
                        {
                            "candidate_id": str(row.candidate_id),
                            "first_name": row.first_name,
                            "last_name": row.last_name,
                            "email": row.email,
                            "similarity_score": float(row.similarity_score),
                        }
                    )

                return candidates

        except Exception as e:
            print(f"Error matching candidates: {str(e)}")
            return []
