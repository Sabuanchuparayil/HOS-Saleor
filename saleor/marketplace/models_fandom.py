"""Fandom features models for marketplace."""

from uuid import uuid4

from django.db import models
from django.utils import timezone

from ..account.models import User
from ..core.models import ModelWithMetadata
from ..product.models import Collection, Product


class FandomCharacter(models.Model):
    """Character from a fandom/universe."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, help_text="Character name")
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Unique slug for the character"
    )
    description = models.TextField(
        blank=True, help_text="Character description/bio"
    )
    image = models.ImageField(
        upload_to="fandom-characters", blank=True, null=True, help_text="Character image"
    )
    fandom_universe = models.CharField(
        max_length=255,
        blank=True,
        help_text="Universe/fandom this character belongs to (e.g., 'Star Wars', 'Marvel')",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this character is currently active"
    )
    featured = models.BooleanField(
        default=False, help_text="Whether to feature this character"
    )

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["slug"], name="character_slug_idx"),
            models.Index(fields=["fandom_universe"], name="character_universe_idx"),
            models.Index(fields=["is_active", "featured"], name="character_active_featured_idx"),
        ]

    def __str__(self):
        return f"{self.name} ({self.fandom_universe})"


class ProductCharacter(models.Model):
    """Association between products and characters."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(
        Product,
        related_name="characters",
        on_delete=models.CASCADE,
        help_text="Product associated with this character",
    )
    character = models.ForeignKey(
        FandomCharacter,
        related_name="products",
        on_delete=models.CASCADE,
        help_text="Character associated with this product",
    )
    is_primary = models.BooleanField(
        default=False, help_text="Whether this is the primary character for this product"
    )

    class Meta:
        ordering = ("-is_primary", "character__name")
        unique_together = [("product", "character")]
        indexes = [
            models.Index(fields=["product"], name="product_char_product_idx"),
            models.Index(fields=["character"], name="product_char_character_idx"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.character.name}"


class Quiz(models.Model):
    """Quiz for fandom engagement."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=255, help_text="Quiz title")
    slug = models.SlugField(
        max_length=255, unique=True, help_text="Unique slug for the quiz"
    )
    description = models.TextField(
        blank=True, help_text="Quiz description"
    )
    questions = models.JSONField(
        default=dict,
        help_text="JSON structure containing quiz questions and answers",
    )
    character = models.ForeignKey(
        FandomCharacter,
        related_name="quizzes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Character this quiz is about",
    )
    collection = models.ForeignKey(
        Collection,
        related_name="quizzes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Collection this quiz is related to",
    )
    points_reward = models.IntegerField(
        default=0,
        help_text="Loyalty points awarded for completing this quiz",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this quiz is currently active"
    )
    featured = models.BooleanField(
        default=False, help_text="Whether to feature this quiz"
    )

    class Meta:
        ordering = ("-featured", "title")
        indexes = [
            models.Index(fields=["slug"], name="quiz_slug_idx"),
            models.Index(fields=["is_active", "featured"], name="quiz_active_featured_idx"),
        ]

    def __str__(self):
        return self.title


class QuizSubmission(models.Model):
    """User's submission/attempt for a quiz."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        User,
        related_name="quiz_submissions",
        on_delete=models.CASCADE,
        help_text="User who took the quiz",
    )
    quiz = models.ForeignKey(
        Quiz,
        related_name="submissions",
        on_delete=models.CASCADE,
        help_text="Quiz that was taken",
    )
    answers = models.JSONField(
        default=dict,
        help_text="JSON structure containing user's answers",
    )
    score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Score/percentage achieved (0-100)",
    )
    points_awarded = models.IntegerField(
        default=0,
        help_text="Loyalty points awarded for this quiz",
    )
    completed_at = models.DateTimeField(
        auto_now_add=True, help_text="When the quiz was completed"
    )

    class Meta:
        ordering = ("-completed_at",)
        indexes = [
            models.Index(fields=["user"], name="quiz_submission_user_idx"),
            models.Index(fields=["quiz"], name="quiz_submission_quiz_idx"),
            models.Index(fields=["completed_at"], name="quiz_submission_completed_idx"),
        ]
        unique_together = [("user", "quiz")]

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} - {self.score}%"




