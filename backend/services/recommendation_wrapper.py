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
RECOMMENDATION_SRC = os.path.join(PROJECT_ROOT, "learning_management_system_lms", "recommendation_system", "src")

HAS_REAL_ENGINE = False

if os.path.exists(RECOMMENDATION_SRC):
    if RECOMMENDATION_SRC not in sys.path:
        sys.path.insert(0, RECOMMENDATION_SRC)
else:
    logger.warning(f"Recommendation SRC not found at {RECOMMENDATION_SRC}")

try:
    import models
    from recommender_engine import ContentBasedRecommender
    from integration_service import LMSIntegrationService
    from data_generator import RealDataLoader, MockDataGenerator
    HAS_REAL_ENGINE = True
    logger.info("Successfully imported Real Recommendation Engine")
except ImportError as e:
    logger.warning(f"Failed to import Recommendation Engine ({e}). Switch to MOCK mode.")
    HAS_REAL_ENGINE = False

class RecommendationServiceWrapper:
    def __init__(self):
        self.service = None
        if HAS_REAL_ENGINE:
            try:
                # Initialize real service
                courses_file = os.path.join(RECOMMENDATION_SRC, "courses.csv")
                if os.path.exists(courses_file):
                    courses = RealDataLoader.load_courses_from_csv(courses_file)
                else:
                    logger.warning("courses.csv not found, generating mock data for Real Engine")
                    courses = MockDataGenerator.generate_courses(50)
                
                recommender = ContentBasedRecommender(courses)
                self.service = LMSIntegrationService(recommender)
                logger.info("Real Recommendation Service initialized")
            except Exception as e:
                logger.error(f"Error initializing Real Engine: {e}. Falling back to Mock.")
                self.service = None
        
        if not self.service:
            logger.info("Using Standalone Mock Service")

    def get_recommendations(self, user_data: Dict) -> Dict:
        """
        Get recommendations from real engine or mock fallback.
        """
        if self.service:
            try:
                return self.service.get_recommendations(user_data)
            except Exception as e:
                logger.error(f"Error getting recommendations from engine: {e}")
                # Fallthrough to mock
        
        # MOCK IMPLEMENTATION
        goal = user_data.get("learning_goal", "General")
        category = user_data.get("preferred_category", "Technology")
        
        logger.info(f"Generating MOCK recommendations for goal: {goal}")
        
        return {
            "user_id": user_data.get("user_id"),
            "recommendations": [
                {
                    "course_id": "MOCK-101",
                    "title": f"Intro to {goal.title()}",
                    "description": f"A comprehensive guide to becoming a {goal}. Perfect for beginners.",
                    "category": category,
                    "difficulty": "Beginner",
                    "duration_hours": 10.5,
                    "match_score": 98.5,
                    "reasons": ["Matches your learning goal", "Highly rated"],
                    "skills_covered": [goal, "Basics", "Fundamentals"],
                    "action_url": "#"
                },
                {
                    "course_id": "MOCK-102",
                    "title": f"Advanced {category} Mastery",
                    "description": f"Deep dive into {category} concepts and applications.",
                    "category": category,
                    "difficulty": "Advanced",
                    "duration_hours": 24.0,
                    "match_score": 85.0,
                    "reasons": ["Matches your category preference"],
                    "skills_covered": ["Advanced Concepts", category, "Project Work"],
                    "action_url": "#"
                }
            ],
            "context": "mock_fallback"
        }

recommendation_service = RecommendationServiceWrapper()
