from typing import Optional, List, Dict
from datetime import datetime
from apps.core.models import Interview, Question, Answer, JobPosting, Candidate
from .base import BaseService


class InterviewService(BaseService):
    """Service for Interview management and intelligent agent logic."""
    
    model = Interview
    
    @classmethod
    def create_interview(cls, job_posting_id: int, candidate_id: int, 
                         channel: str = 'web') -> Optional[Interview]:
        """Create a new interview session."""
        from .job_service import JobService
        from .candidate_service import CandidateService
        
        job = JobService.get_by_id(job_posting_id)
        candidate = CandidateService.get_by_id(candidate_id)
        
        if not job or not candidate:
            return None
        
        # Calculate initial skill match score
        skill_match = cls._calculate_skill_match(job, candidate)
        
        interview = cls.model.objects.create(
            job_posting=job,
            candidate=candidate,
            channel=channel,
            skill_match_score=skill_match,
            status='pending'
        )
        return interview
    
    @classmethod
    def start_interview(cls, interview_id: int) -> Optional[Interview]:
        """Start an interview and generate initial questions."""
        interview = cls.get_by_id(interview_id)
        if not interview or interview.status != 'pending':
            return None
        
        interview.status = 'in_progress'
        interview.started_at = datetime.now()
        interview.save()
        
        # Generate adaptive questions based on job requirements
        cls._generate_questions(interview)
        
        return interview
    
    @classmethod
    def submit_answer(cls, question_id: int, answer_text: str) -> Optional[Answer]:
        """Submit an answer to a question."""
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return None
        
        # Evaluate the answer
        score = cls._evaluate_answer(question, answer_text)
        
        answer = Answer.objects.create(
            question=question,
            answer_text=answer_text,
            score=score
        )
        
        # Check if all questions are answered
        interview = question.interview
        total_questions = interview.questions.count()
        answered_questions = Answer.objects.filter(question__interview=interview).count()
        
        if answered_questions == total_questions:
            cls._complete_interview(interview)
        
        return answer
    
    @classmethod
    def complete_interview(cls, interview_id: int) -> Optional[Interview]:
        """Manually complete an interview."""
        interview = cls.get_by_id(interview_id)
        if interview:
            return cls._complete_interview(interview)
        return None
    
    @classmethod
    def _calculate_skill_match(cls, job: JobPosting, candidate: Candidate) -> float:
        """Calculate skill match percentage between job requirements and candidate skills."""
        required_skills = set(skill.lower() for skill in job.required_skills)
        candidate_skills = set(skill.lower() for skill in candidate.skills)
        
        if not required_skills:
            return 0.0
        
        matched_skills = required_skills.intersection(candidate_skills)
        match_percentage = (len(matched_skills) / len(required_skills)) * 100
        
        return round(match_percentage, 2)
    
    @classmethod
    def _generate_questions(cls, interview: Interview) -> List[Question]:
        """Generate adaptive questions based on job requirements and candidate profile."""
        questions = []
        job = interview.job_posting
        candidate = interview.candidate
        
        # Generate questions for each required skill
        for idx, skill in enumerate(job.required_skills[:5], 1):  # Limit to 5 questions
            difficulty = cls._determine_difficulty(skill, candidate)
            
            question = Question.objects.create(
                interview=interview,
                question_text=f"Can you describe your experience with {skill}?",
                difficulty=difficulty,
                skill_evaluated=skill,
                expected_answer_keywords=[skill.lower(), 'experience', 'project'],
                order=idx
            )
            questions.append(question)
        
        return questions
    
    @classmethod
    def _determine_difficulty(cls, skill: str, candidate: Candidate) -> str:
        """Determine question difficulty based on candidate's experience."""
        if skill.lower() in [s.lower() for s in candidate.skills]:
            return 'hard'
        elif candidate.experience_years >= 3:
            return 'medium'
        else:
            return 'easy'
    
    @classmethod
    def _evaluate_answer(cls, question: Question, answer_text: str) -> float:
        """Evaluate an answer based on expected keywords and quality."""
        answer_lower = answer_text.lower()
        keywords_found = sum(1 for keyword in question.expected_answer_keywords 
                            if keyword in answer_lower)
        
        # Simple scoring: base score + keyword bonus
        base_score = 5.0
        keyword_bonus = (keywords_found / max(len(question.expected_answer_keywords), 1)) * 3.0
        length_bonus = min(len(answer_text.split()) / 50, 2.0)  # Up to 2 points for length
        
        total_score = min(base_score + keyword_bonus + length_bonus, 10.0)
        return round(total_score, 2)
    
    @classmethod
    def _complete_interview(cls, interview: Interview) -> Interview:
        """Complete the interview and calculate final score."""
        interview.status = 'completed'
        interview.completed_at = datetime.now()
        
        # Calculate final score
        answers = Answer.objects.filter(question__interview=interview)
        if answers.exists():
            avg_answer_score = sum(a.score or 0 for a in answers) / answers.count()
            # Final score: 40% skill match + 60% interview performance
            final_score = (interview.skill_match_score * 0.4) + (avg_answer_score * 10 * 0.6)
            interview.final_score = round(final_score, 2)
            
            # Generate recommendation
            interview.agent_recommendation = cls._generate_recommendation(interview, final_score)
        
        interview.save()
        return interview
    
    @classmethod
    def _generate_recommendation(cls, interview: Interview, final_score: float) -> str:
        """Generate agent recommendation based on interview performance."""
        if final_score >= 80:
            return "Highly Recommended: Excellent match with strong technical skills."
        elif final_score >= 60:
            return "Recommended: Good candidate with solid qualifications."
        elif final_score >= 40:
            return "Consider with Caution: Meets basic requirements but may need development."
        else:
            return "Not Recommended: Significant gaps in required skills and experience."
    
    @classmethod
    def get_interviews_by_job(cls, job_id: int):
        """Get all interviews for a specific job posting."""
        return cls.model.objects.filter(job_posting_id=job_id)
    
    @classmethod
    def get_interviews_by_candidate(cls, candidate_id: int):
        """Get all interviews for a specific candidate."""
        return cls.model.objects.filter(candidate_id=candidate_id)
