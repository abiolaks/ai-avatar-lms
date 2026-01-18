import sys
import os
import logging
from typing import Dict, List

# logger configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_avatar_backend.recommendation")

# Add the project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Construct path to recommendation engine src
# Structure: backend/services/../../learning_management_system_lms/recommendation_system/src
RECOMMENDATION_SRC = os.path.join(PROJECT_ROOT, "learning_management_system_lms", "recommendation_system", "src")

logger.info(f"Project Root: {PROJECT_ROOT}")
logger.info(f"Recommendation SRC Path: {RECOMMENDATION_SRC}")

if os.path.exists(RECOMMENDATION_SRC):
    if RECOMMENDATION_SRC not in sys.path:
        sys.path.insert(0, RECOMMENDATION_SRC) # Insert at beginning to prioritize
        logger.info(f"Added {RECOMMENDATION_SRC} to sys.path")
else:
    logger.error(f"Path does not exist: {RECOMMENDATION_SRC}")
    # Fallback/Debug: List directories in project root
    try:
        logger.info(f"Contents of {PROJECT_ROOT}: {os.listdir(PROJECT_ROOT)}")
        lms_path = os.path.join(PROJECT_ROOT, "learning_management_system_lms")
        if os.path.exists(lms_path):
             logger.info(f"Contents of {lms_path}: {os.listdir(lms_path)}")
    except Exception as e:
        logger.error(f"Could not list directories: {e}")

try:
    # Try importing models first to verify path
    import models
    logger.info("Successfully imported models")
    from recommender_engine import ContentBasedRecommender
    from integration_service import LMSIntegrationService
    from data_generator import RealDataLoader, MockDataGenerator
    logger.info("Successfully imported recommendation modules")
except ImportError as e:
    logger.error(f"Failed to import recommendation modules: {e}")
    # Attempt to print sys.path for debugging
    logger.error(f"sys.path: {sys.path}")
    raise

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
