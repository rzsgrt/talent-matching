from uuid import UUID, uuid4

from config import DB_CONFIG, MODEL
from fastapi import BackgroundTasks, FastAPI, HTTPException
from schemas.candidate_schema import CandidateCreate
from schemas.job_schema import JobCreate
from services.candidate_service import CandidateService
from services.job_service import JobService
from sqlalchemy.exc import SQLAlchemyError
from utils.database import Database
from models.job_model import JobModel
from models.candidate_model import CandidateModel
from utils.candidate_match import CandidateMatch

app = FastAPI()

# Initialize services
database = Database(**DB_CONFIG)
job_service = JobService(database, MODEL)
candidate_service = CandidateService(database, MODEL)


@app.post("/insert-job")
async def insert_job(
    job_data: JobCreate, background_tasks: BackgroundTasks
) -> dict:
    job_id = uuid4()

    background_tasks.add_task(
        job_service.process_job, job_id=job_id, job_data=job_data.dict()
    )

    return {
        "success": True,
        "job_id": str(job_id),
        "message": "Job processing started",
    }


@app.post("/update-job/{previous_job_id}")
async def update_job(
    previous_job_id: UUID,
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
) -> dict:
    new_job_id = uuid4()

    background_tasks.add_task(
        job_service.update_job,
        new_job_id=new_job_id,
        previous_job_id=previous_job_id,
        job_data=job_data.dict(),
    )

    return {
        "success": True,
        "previous_job_id": str(previous_job_id),
        "new_job_id": str(new_job_id),
        "message": "Job update started",
    }


@app.post("/insert-candidate")
async def insert_candidate(
    candidate_data: CandidateCreate, background_tasks: BackgroundTasks
) -> dict:
    candidate_id = uuid4()

    background_tasks.add_task(
        candidate_service.process_candidate,
        candidate_id=candidate_id,
        candidate_data=CandidateCreate.dict(),
    )

    return {
        "success": True,
        "candidate_id": str(candidate_id),
        "message": "Job processing started",
    }


@app.post("/update-candidate/{candidate_id}")
async def update_candidate(
    candidate_id: UUID,
    candidate_data: CandidateCreate,
    background_tasks: BackgroundTasks,
) -> dict:

    background_tasks.add_task(
        candidate_service.update_candidate,
        candidate_id=candidate_id,
        candidate_data=candidate_data.dict(),
    )

    return {
        "success": True,
        "message": "Candidate update started",
    }


@app.get("/check-job/{job_id}")
def check_job_status(job_id: UUID) -> dict:
    """Check job status and version history."""
    try:
        with database.get_session() as session:
            # Get job by id
            job = (
                session.query(JobModel)
                .filter(JobModel.job_id == job_id)
                .first()
            )

            if not job:
                raise HTTPException(
                    status_code=404, detail=f"Job with ID {job_id} not found"
                )

            return {
                "job_id": str(job_id),
                "versions": [
                    {
                        "job_id": str(job.job_id),
                        "status": job.status,
                        "previous_version_id": (
                            str(job.previous_version_id)
                            if job.previous_version_id
                            else None
                        ),
                        "created_at": job.created_at,
                        "updated_at": job.updated_at,
                    }
                ],
            }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/check-candidate/{candidate_id}")
def check_candidate_status(candidate_id: UUID) -> dict:
    """Check if candidate exists in database."""
    try:
        with database.get_session() as session:
            candidate = (
                session.query(CandidateModel)
                .filter(CandidateModel.candidate_id == candidate_id)
                .first()
            )

            if not candidate:
                raise HTTPException(
                    status_code=404,
                    detail=f"Candidate with ID {candidate_id} not found",
                )

            return {
                "exists": True,
                "candidate_id": str(candidate_id),
                "created_at": candidate.created_at,
                "updated_at": candidate.updated_at,
            }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/match-candidates/{job_id}")
def match_candidates(
    job_id: UUID, total_candidate: int = 10  # default value
) -> dict:
    """Get matching candidates for a job.

    Args:
        job_id: Job to match candidates against
        total_candidate: Number of top candidates to return
    """
    try:
        matcher = CandidateMatch(database)
        matches = matcher.get_candidates_by_job(
            job_id=job_id, total_candidate=total_candidate
        )

        return {
            "job_id": str(job_id),
            "total_candidates": len(matches),
            "candidates": matches,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error matching candidates: {str(e)}"
        )
