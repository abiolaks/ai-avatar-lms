import logging
import re
from typing import Dict, Optional, Tuple
from .recommendation_wrapper import recommendation_service

logger = logging.getLogger("ai_avatar_backend.nlu")

class NLUService:
    """
    Simple NLU service for MVP.
    Extracts intent and entities using regex/keywords.
    """
    
    def __init__(self):
        pass

    def process_text(self, text: str, user_id: str = "U001") -> Dict:
        """
        Process user text and return a response action.
        """
        logger.info(f"Processing text: {text}")
        
        intent, entities = self._classify_intent(text)
        logger.info(f"Detected intent: {intent}, entities: {entities}")
        
        response = {
            "text": "I'm not sure I understood that.",
            "action": None,
            "data": None
        }

        if intent == "learning_goal":
            # Call specific recommendation logic
            # For now, we construct a user profile update based on the goal
            # This is a simplification. In a real app, we'd fetch the user profile first.
            
            # Mock user data update
            if entities.get("goal"):
                # We need to adapt this to calls to recommendation_wrapper
                # But recommendation wrapper takes full user data.
                # For this MVP, let's create a dummy user with this goal.
                
                user_data = {
                    "user_id": user_id,
                    "name": "Current User",
                    "job_role": "Learner",
                    "department": "General",
                    "skill_level": "Beginner",
                    "learning_goal": entities["goal"],
                    "preferred_category": "Data Science" if "data" in entities["goal"].lower() else "Business",
                    "preferred_difficulty": "Beginner",
                    "preferred_duration": "Medium",
                    "known_skills": [],
                    "enrolled_courses": []
                }
                
                try:
                    recs = recommendation_service.get_recommendations(user_data)
                    top_course = recs['recommendations'][0] if recs['recommendations'] else None
                    
                    if top_course:
                        course_title = top_course['title']
                        response["text"] = f"I found a great course for you: {course_title}. It matches your goal to become a {entities['goal']}."
                        response["action"] = "recommend_course"
                        response["data"] = recs
                    else:
                        response["text"] = f"I processed your goal to become a {entities['goal']}, but couldn't find a specific course yet."
                except Exception as e:
                    logger.error(f"Recommendation failed: {e}")
                    response["text"] = "I had trouble getting recommendations right now."
                    
        elif intent == "greeting":
            response["text"] = "Hello! I am your AI learning assistant. Tell me, what do you want to learn today?"
            
        return response

    def _classify_intent(self, text: str) -> Tuple[str, Dict]:
        text = text.lower()
        
        # Simple keyword matching
        if any(word in text for word in ["hello", "hi", "hey"]):
            return "greeting", {}
        
        # Regex for "I want to become a [Goal]" or "I want to learn [Skill]"
        goal_match = re.search(r"i want to (?:become|be) (?:a|an) (.+)", text)
        if goal_match:
            return "learning_goal", {"goal": goal_match.group(1).strip()}
            
        learn_match = re.search(r"i want to learn (.+)", text)
        if learn_match:
             return "learning_goal", {"goal": learn_match.group(1).strip()}

        return "unknown", {}

nlu_service = NLUService()
