"""Utility functions for fandom features."""

from typing import Optional

from django.utils import timezone

from ..account.models import User
from . import models_fandom


def submit_quiz(user: User, quiz: "Quiz", answers: dict) -> "QuizSubmission":
    """Submit a quiz and calculate score, award points if applicable."""
    from .models_fandom import QuizSubmission

    # Calculate score (simplified - in production, implement proper scoring logic)
    score = calculate_quiz_score(quiz, answers)

    # Award points if quiz has points reward
    points_awarded = 0
    if quiz.points_reward > 0 and score >= 50:  # Minimum 50% to get points
        from .utils_loyalty import create_points_transaction
        from .models_loyalty import LoyaltyPointsTransaction
        
        create_points_transaction(
            user,
            quiz.points_reward,
            LoyaltyPointsTransaction.TransactionType.EARNED,
            description=f"Points for completing quiz: {quiz.title}",
        )
        points_awarded = quiz.points_reward

    # Create or update submission (only one submission per user per quiz)
    submission, created = QuizSubmission.objects.get_or_create(
        user=user,
        quiz=quiz,
        defaults={
            "answers": answers,
            "score": score,
            "points_awarded": points_awarded,
            "completed_at": timezone.now(),
        },
    )

    if not created:
        # Update existing submission
        submission.answers = answers
        submission.score = score
        submission.points_awarded = points_awarded
        submission.completed_at = timezone.now()
        submission.save(update_fields=["answers", "score", "points_awarded", "completed_at"])

    return submission


def calculate_quiz_score(quiz, answers: dict) -> int:
    """Calculate score for a quiz submission.
    
    This is a simplified implementation. In production, you would:
    - Parse the quiz.questions JSON structure
    - Compare user answers with correct answers
    - Calculate percentage score
    
    For now, returns a placeholder score.
    """
    # TODO: Implement proper scoring logic based on quiz.questions structure
    # This is a placeholder that returns a fixed score
    # In production, parse quiz.questions and compare with answers
    
    if not quiz.questions or not answers:
        return 0
    
    # Placeholder: return 75% as default
    # In production, implement proper comparison
    return 75

