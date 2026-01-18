import sys
import os
import logging
from typing import Dict, List

# Add the project root to sys.path to allow importing from learning_management_system_lms
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from learning_management_system_lms.recommendation_system.src.recommender_engine import ContentBasedRecommender
from learning_management_system_lms.recommendation_system.src.integration_service import LMSIntegrationService
from learning_management_system_lms.recommendation_system.src.data_generator import RealDataLoader, MockDataGenerator

logger = logging.getLogger("ai_avatar_backend.recommendation")

class RecommendationServiceWrapper:
    def __init__(self):
        self.lms_service = None
        self._initialize()

    def _initialize(self):
        try:
            # Path to courses.csv
            courses_path = os.path.join(PROJECT_ROOT, "learning_management_system_lms", "recommendation_system", "src", "courses.csv")
            
            if os.path.exists(courses_path):
                logger.info(f"Loading courses from {courses_path}")
                courses = RealDataLoader.load_courses_from_csv(courses_path)
            else:
                logger.warning(f"courses.csv not found at {courses_path}, generating mock data")
                courses = MockDataGenerator.generate_courses(100)
            
            recommender = ContentBasedRecommender(courses)
            self.lms_service = LMSIntegrationService(recommender)
            logger.info("Recommendation Service Initialized Successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Recommendation Service: {e}")
            raise

    def get_recommendations(self, user_data: Dict, context: str = "ai_avatar") -> Dict:
        """
        Get recommendations for a user.
        user_data should be a dictionary matching the structure expected by LMSIntegrationService.
        """
        if not self.lms_service:
            raise RuntimeError("Recommendation Service not initialized")
        
        return self.lms_service.get_recommendations(user_data, context=context)

# Singleton instance
recommendation_service = RecommendationServiceWrapper()
