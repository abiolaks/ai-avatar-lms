import sys
import os
import logging
from typing import Dict

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# The assessment generator seems to assume it's running from its own directory due to imports like 'from modules.cleaner'
# We might need to handle sys.path carefully or modify the imports in the assessment generator if it fails.
# For now, let's try to append the assessment directory to sys.path as well.
ASSESSMENT_DIR = os.path.join(PROJECT_ROOT, "learning_management_system_lms", "assements_generator")
if ASSESSMENT_DIR not in sys.path:
    sys.path.append(ASSESSMENT_DIR)

try:
    from learning_management_system_lms.assements_generator.main import run_pipeline
except ImportError:
    # Fallback: try importing directly if modules are in path
    from main import run_pipeline

logger = logging.getLogger("ai_avatar_backend.assessment")

class AssessmentServiceWrapper:
    
    def generate_assessment(self, transcript: str) -> Dict:
        """
        Generates an assessment from a transcript.
        """
        logger.info("Generating assessment from transcript...")
        try:
            result = run_pipeline(transcript)
            return result
        except Exception as e:
            logger.error(f"Error generating assessment: {e}")
            raise

# Singleton instance
assessment_service = AssessmentServiceWrapper()
