from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import List
from api.schemas import (
    InterviewCreate, InterviewResponse, InterviewDetailResponse,
    QuestionResponse, AnswerCreate, AnswerResponse
)
from api.dependencies import (
    get_interview_service, get_current_user, get_current_candidate,
    InterviewService
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    data: InterviewCreate,
    background_tasks: BackgroundTasks,
    candidate = Depends(get_current_candidate),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Create a new interview session (Candidate only)."""
    interview = interview_service.create_interview(
        job_posting_id=data.job_posting_id,
        candidate_id=candidate.id,
        channel=data.channel
    )
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create interview"
        )
    
    # Schedule async question generation
    from apps.core.tasks import generate_interview_questions
    background_tasks.add_task(generate_interview_questions.delay, interview.id)
    
    return InterviewResponse.model_validate(interview)


@router.get("", response_model=List[InterviewResponse])
def list_interviews(
    user = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """List interviews based on user role."""
    if user.role == 'candidate':
        from api.dependencies import CandidateService
        candidate = CandidateService.get_by_user_id(user.id)
        interviews = interview_service.get_interviews_by_candidate(candidate.id)
    elif user.role == 'company':
        from api.dependencies import CompanyService, JobService
        company = CompanyService.get_by_user_id(user.id)
        jobs = JobService.get_jobs_by_company(company.id)
        interviews = []
        for job in jobs:
            interviews.extend(interview_service.get_interviews_by_job(job.id))
    else:
        interviews = interview_service.get_all()
    
    return [InterviewResponse.model_validate(i) for i in interviews]


@router.get("/{interview_id}", response_model=InterviewDetailResponse)
def get_interview(
    interview_id: int,
    user = Depends(get_current_user),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Get interview details with questions."""
    interview = interview_service.get_by_id(interview_id)
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check permissions
    if user.role == 'candidate' and interview.candidate.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this interview"
        )
    elif user.role == 'company' and interview.job_posting.company.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this interview"
        )
    
    questions = list(interview.questions.all())
    
    return InterviewDetailResponse(
        **InterviewResponse.model_validate(interview).model_dump(),
        questions=[QuestionResponse.model_validate(q) for q in questions]
    )


@router.post("/{interview_id}/start", response_model=InterviewResponse)
def start_interview(
    interview_id: int,
    candidate = Depends(get_current_candidate),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Start an interview session (Candidate only)."""
    interview = interview_service.get_by_id(interview_id)
    
    if not interview or interview.candidate.user_id != candidate.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to start this interview"
        )
    
    interview = interview_service.start_interview(interview_id)
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to start interview"
        )
    
    return InterviewResponse.model_validate(interview)


@router.post("/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
def submit_answer(
    data: AnswerCreate,
    candidate = Depends(get_current_candidate),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Submit an answer to an interview question (Candidate only)."""
    answer = interview_service.submit_answer(
        question_id=data.question_id,
        answer_text=data.answer_text
    )
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit answer"
        )
    
    return AnswerResponse.model_validate(answer)


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
def complete_interview(
    interview_id: int,
    background_tasks: BackgroundTasks,
    candidate = Depends(get_current_candidate),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """Complete an interview and calculate final score (Candidate only)."""
    interview = interview_service.get_by_id(interview_id)
    
    if not interview or interview.candidate.user_id != candidate.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to complete this interview"
        )
    
    # Schedule async score calculation
    from apps.core.tasks import calculate_final_score
    background_tasks.add_task(calculate_final_score.delay, interview_id)
    
    return InterviewResponse.model_validate(interview)
