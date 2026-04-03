"""Automation workflow definitions."""

from src.workflows.affiliate import AffiliateWorkflow
from src.workflows.content_gen import ContentGenerationWorkflow
from src.workflows.social_media import SocialMediaWorkflow

__all__ = ["AffiliateWorkflow", "ContentGenerationWorkflow", "SocialMediaWorkflow"]
