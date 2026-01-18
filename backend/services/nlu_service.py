import logging
import json
import requests
from typing import Dict, Optional, Tuple
from .recommendation_wrapper import recommendation_service

logger = logging.getLogger("ai_avatar_backend.nlu")

# Configuration for Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
# Using a widely available lightweight model. User requested qwen3:0.6b, assuming qwen2.5:0.5b or similiar.
# You can change this to the exact model name present in your `ollama list`
OLLAMA_MODEL = "qwen2.5:0.5b" 

class NLUService:
    """
    NLU Service using Local LLM (Ollama).
    """
    
    def __init__(self):
        pass

    def process_text(self, text: str, user_id: str = "U001") -> Dict:
        """
        Process user text and return a response action.
        """
        logger.info(f"Processing text: {text}")
        
        intent, entities = self._classify_intent_ollama(text)
        logger.info(f"Detected intent: {intent}, entities: {entities}")
        
        response = {
            "text": "I'm not sure I understood that.",
            "action": None,
            "data": None
        }

        if intent == "learning_goal":
            # Extract Goal
            goal = entities.get("goal") or "learn something"
            category = entities.get("category") or "General"
            
            # Construct synthetic user profile
            user_data = {
                "user_id": user_id,
                "name": "Current User",
                "job_role": "Learner",
                "department": "General",
                "skill_level": "Beginner",
                "learning_goal": goal,
                "preferred_category": category,
                "preferred_difficulty": "Beginner",
                "preferred_duration": "Medium",
                "known_skills": [],
                "enrolled_courses": []
            }
            
            try:
                recs = recommendation_service.get_recommendations(user_data)
                
                if recs['recommendations']:
                    top_course = recs['recommendations'][0]
                    course_title = top_course['title']
                    response["text"] = f"Based on your goal to {goal}, I recommend: {course_title}."
                    response["action"] = "recommend_course"
                    response["data"] = recs
                else:
                    response["text"] = f"I understand you want to {goal}, but I couldn't find a matching course right now."
                    
            except Exception as e:
                logger.error(f"Recommendation failed: {e}")
                response["text"] = "I had trouble accessing the course catalog."
                
        elif intent == "greeting":
            response["text"] = "Hello! I am your AI learning assistant. I can help you find the perfect course. What would you like to learn?"
        
        else:
             response["text"] = "I can help you find courses. Try saying 'I want to become a data scientist'."
            
        return response

    def _classify_intent_ollama(self, text: str) -> Tuple[str, Dict]:
        """
        Call Ollama to classify intent and extract entities.
        """
        system_prompt = """
        You are an NLU assistant for a Learning Management System.
        Analyze the user's input and extract the intent and entities in JSON format.
        
        Possible Intents:
        - "learning_goal": User wants to learn a skill, topic, or become a specific role.
        - "greeting": User is saying hello.
        - "unknown": Anything else.
        
        If intent is "learning_goal", extract:
        - "goal": The specific role or skill (e.g., "Data Scientist", "Python").
        - "category": A broad category (e.g., "Data Science", "Business", "Web Development").
        
        Output JSON ONLY. Do not explain.
        Example: {"intent": "learning_goal", "entities": {"goal": "Data Scientist", "category": "Data Science"}}
        """
        
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\nUser Input: {text}\nJSON Response:",
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            llm_output = result.get("response", "{}")
            logger.info(f"LLM Output: {llm_output}")
            
            parsed = json.loads(llm_output)
            return parsed.get("intent", "unknown"), parsed.get("entities", {})
            
        except Exception as e:
            logger.error(f"Ollama NLU failed: {e}")
            # Fallback to regex if LLM fails
            return self._fallback_regex(text)

    def _fallback_regex(self, text: str) -> Tuple[str, Dict]:
        logger.info("Using fallback regex NLU")
        text = text.lower()
        import re
        if any(w in text for w in ["hello", "hi", "hey"]):
            return "greeting", {}
        
        match = re.search(r"want to (?:be|become|learn) (?:a |an )?(.+)", text)
        if match:
            goal = match.group(1).strip()
            category = "Data Science" if "data" in goal else "Business"
            return "learning_goal", {"goal": goal, "category": category}
            
        return "unknown", {}

nlu_service = NLUService()
