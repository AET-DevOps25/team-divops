# Standard library imports
import json
import os
import random
import uuid
from datetime import datetime
from typing import List, Tuple, Optional
import ast

# Third-party imports
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from google import genai
from google.genai import types
import weaviate
from weaviate.classes.query import Filter, Sort

# Local imports
from app.models import TarotCard, Discussion, FollowupQuestion, CardLayout
from app.prompt_loader import load_tarot_template, render_prompt, build_tarot_prompt_smart
from app.card_engine import layout_three_card
from app.logger_config import get_tarot_logger
from app.weaviate_client import get_weaviate_client
from app.context_aware_reading import enhance_reading_with_feedback_context


# Setup logger
logger = get_tarot_logger(__name__)


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def check_environment_variables():
    if not API_KEY :
        raise RuntimeError("Missing GEMINI_API_KEY in environment")

def fetch_full_deck() -> List[TarotCard]:
    """Fetch all tarot cards from Weaviate"""
    logger.info("Fetching full tarot deck from Weaviate")
    client = get_weaviate_client()
    try:
        tarot_col = client.collections.get("TarotCard")
        # Use the correct API method
        all_objs = tarot_col.query.fetch_objects(limit=78)  # 78 cards in a tarot deck
        
        cards = []
        for obj in all_objs.objects:
            card_data = {
                "name": obj.properties.get("name", ""),
                "arcana": obj.properties.get("arcana", ""),
                "meanings_light": obj.properties.get("meanings_light", []),
                "meanings_shadow": obj.properties.get("meanings_shadow", []),
                "keywords": obj.properties.get("keywords", []),
                "fortune_telling": obj.properties.get("fortune_telling", []),
            }
            cards.append(TarotCard(**card_data))
        
        logger.info(f"Successfully fetched {len(cards)} tarot cards")
        return cards
    except Exception as e:
        logger.error(f"Error fetching deck: {e}")
        return []

def build_tarot_prompt(question: str, picks):
    template_str = load_tarot_template()  
    return render_prompt(template_str, question, picks)

def build_tarot_prompt_with_history(question: str, picks, history: List[dict] = None):
    """
    Build tarot prompt with optional conversation history.
    Uses the smart prompt builder from prompt_loader.
    """
    return build_tarot_prompt_smart(question, picks, history)

def call_gemini_api(prompt: str) -> str:
    """
    Call the Gemini API with the provided prompt and return the response.
    """
    logger.info("Calling Gemini API for content generation")
    check_environment_variables()
    
    try:
        # Load the configuration from the JSON file
        with open(os.path.join(os.path.dirname(__file__), "gemini_config.json"), "r", encoding="utf-8") as f:
            cfg = json.load(f)

        gen_cfg = types.GenerationConfig(**cfg["generation_config"])
        safe_cfg = [types.SafetySetting(**s) for s in cfg["safety_settings"]]

        gen_cfg = types.GenerateContentConfig(
            **cfg["generation_config"],
            safety_settings=safe_cfg,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        )

        client = genai.Client(api_key = API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=gen_cfg
        )
        
        logger.info(f"Successfully generated content with Gemini API (response length: {len(response.text) if response.text else 0} characters)")
        return response.text
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise 

def call_gemini_api_with_history(question: str, picks, history: List[dict] = None) -> str:
    """
    Call the Gemini API with tarot prompt that includes conversation history.
    This is a convenience function that combines prompt building and API calling.
    """
    prompt = build_tarot_prompt_with_history(question, picks, history)
    return call_gemini_api(prompt)

def store_feedback(user_id: str, question: str, feedback: str) -> None:
    """Store user feedback for a question in a local JSON file (feedback.json)."""
    logger.info(f"Storing feedback for user {user_id} on question '{question}': {feedback}")
    feedback_entry = {
        "user_id": user_id,
        "question": question,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }
    feedback_file = os.path.join(os.path.dirname(__file__), "feedback.json")
    try:
        # Read existing feedbacks
        if os.path.exists(feedback_file):
            with open(feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = []
        else:
            data = []
        # Append new feedback
        data.append(feedback_entry)
        # Write back
        with open(feedback_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Feedback stored successfully.")
    except Exception as e:
        logger.error(f"Failed to store feedback: {e}")

def store_discussion(discussion: Discussion, client) -> None:
    """
    sture a discussion in Weaviate.
    """
    try:
        if not client.collections.exists("Discussion"):
            client.collections.create(
                name="Discussion",
                properties=[
                    weaviate.classes.config.Property(
                        name="discussion_id",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="user_id",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="created_at",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="initial_question",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="initial_response",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="cards_drawn",
                        data_type=weaviate.classes.config.DataType.TEXT
                    )
                ]
            )
        
        discussion_col = client.collections.get("Discussion")
        discussion_col.data.insert(
            properties={
                "discussion_id": discussion.discussion_id,
                "user_id": discussion.user_id,
                "created_at": discussion.created_at.isoformat(),
                "initial_question": discussion.initial_question,
                "initial_response": discussion.initial_response,
                "cards_drawn": json.dumps([card.model_dump() for card in discussion.cards_drawn])
            }
        )
        print(f"Stored discussion: {discussion.discussion_id}")
    except Exception as e:
        print(f"Error storing discussion: {e}")

def get_discussion(discussion_id: str, client) -> Optional[Discussion]:
    try:
        if not client.collections.exists("Discussion"):
            print("[DEBUG] Discussion collection does not exist")
            return None

        discussion_col = client.collections.get("Discussion")
        try:
            result = discussion_col.query.fetch_objects(
                where=Filter.by_property("discussion_id").equal(discussion_id),
                limit=1
            )
        except Exception as e:
            print(f"[DEBUG] Where query not supported, fallback to full scan: {e}")
            result = discussion_col.query.fetch_objects(limit=1000)

        found_discussion = None
        for obj in result.objects:
            print(f"[DEBUG] Found discussion_id in DB: {obj.properties.get('discussion_id')}")
            if obj.properties.get("discussion_id") == discussion_id:
                found_discussion = obj
                break

        if found_discussion:
            props = found_discussion.properties
            cards_drawn = []
            if props.get("cards_drawn"):
                cards_drawn = parse_cards_drawn(props.get("cards_drawn"))
            discussion_data = {
                "discussion_id": props.get("discussion_id"),
                "user_id": props.get("user_id"),
                "created_at": datetime.fromisoformat(props.get("created_at")),
                "initial_question": props.get("initial_question"),
                "initial_response": props.get("initial_response"),
                "cards_drawn": cards_drawn
            }
            return Discussion(**discussion_data)
        print("[DEBUG] No matching discussion_id found")
        return None
    except Exception as e:
        print(f"Error getting discussion: {e}")
        return None

def store_followup_question(followup: FollowupQuestion, client) -> None:
    """
    Store a followup question in Weaviate."""
    try:
        if not client.collections.exists("FollowupQuestion"):
            client.collections.create(
                name="FollowupQuestion",
                properties=[
                    weaviate.classes.config.Property(
                        name="question_id",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="discussion_id",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="question",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="response",
                        data_type=weaviate.classes.config.DataType.TEXT
                    ),
                    weaviate.classes.config.Property(
                        name="timestamp",
                        data_type=weaviate.classes.config.DataType.TEXT
                    )
                ]
            )
        
        followup_col = client.collections.get("FollowupQuestion")
        followup_col.data.insert(
            properties={
                "question_id": followup.question_id,
                "discussion_id": followup.discussion_id,
                "question": followup.question,
                "response": followup.response,
                "timestamp": followup.timestamp.isoformat()
            }
        )
        print(f"Stored followup question: {followup.question_id}")
    except Exception as e:
        print(f"Error storing followup question: {e}")

def get_discussion_history(discussion_id: str, client) -> List[FollowupQuestion]:
    """
    Get the discussion history for a given discussion ID.
    """
    try:
        if not client.collections.exists("FollowupQuestion"):
            return []
            
        followup_col = client.collections.get("FollowupQuestion")
        result = followup_col.query.fetch_objects(
            limit=100  # Reasonable limit to avoid fetching too many objects
        )
        
        # Filter manually and sort by timestamp
        filtered_followups = []
        for obj in result.objects:
            if obj.properties.get("discussion_id") == discussion_id:
                filtered_followups.append(obj)
        
        # Sort by timestamp
        filtered_followups.sort(key=lambda x: x.properties.get("timestamp", ""))
        
        followups = []
        for obj in filtered_followups:
            props = obj.properties
            followup_data = {
                "question_id": props.get("question_id"),
                "discussion_id": props.get("discussion_id"),
                "question": props.get("question"),
                "response": props.get("response"),
                "timestamp": datetime.fromisoformat(props.get("timestamp")),
                "cards_drawn": []  
            }
            followups.append(FollowupQuestion(**followup_data))
        
        return followups
    except Exception as e:
        print(f"Error getting discussion history: {e}")
        return []

def build_followup_prompt(question: str, original_cards: List[CardLayout], history: List[FollowupQuestion]) -> str:
    """
    Build followup prompt using the original cards from the discussion.
    TODO: Implement context-aware reading enhancement
    """
    context = ""
    if history:
        context = "Previous conversation context:\n"
        for i, h in enumerate(history, 1):
            context += f"Q{i}: {h.question}\nA{i}: {h.response}\n\n"

    picks = original_cards[:3]

    base_prompt = build_tarot_prompt(question, picks)

    if context:
        return f"{context}\nCurrent question based on the same cards:\n{base_prompt}"
    else:
        return base_prompt

def call_gemini_api_followup(question: str, original_cards: List[CardLayout], history: List[FollowupQuestion] = None) -> str:
    """
    Call the Gemini API for followup questions using original cards from the discussion.
    """
    prompt = build_followup_prompt(question, original_cards, history)
    return call_gemini_api(prompt)

def get_user_discussions_list(user_id: str, client) -> List[Discussion]:
    try:
        if not client.collections.exists("Discussion"):
            return []
            
        discussion_col = client.collections.get("Discussion")
        result = discussion_col.query.fetch_objects(
            limit=1000  # Higher limit for user discussions
        )
        
        # Filter manually and sort by created_at
        filtered_discussions = []
        for obj in result.objects:
            if obj.properties.get("user_id") == user_id:
                filtered_discussions.append(obj)
        
        # Sort by created_at (descending - most recent first)
        filtered_discussions.sort(key=lambda x: x.properties.get("created_at", ""), reverse=True)
        
        discussions = []
        for obj in filtered_discussions:
            props = obj.properties
            
            cards_drawn = []
            if props.get("cards_drawn"):
                cards_drawn = parse_cards_drawn(props.get("cards_drawn"))
            
            discussion_data = {
                "discussion_id": props.get("discussion_id"),
                "user_id": props.get("user_id"),
                "created_at": datetime.fromisoformat(props.get("created_at")),
                "initial_question": props.get("initial_question"),
                "initial_response": props.get("initial_response"),
                "cards_drawn": cards_drawn
            }
            discussions.append(Discussion(**discussion_data))
        
        return discussions
    except Exception as e:
        print(f"Error getting user discussions: {e}")
        return []

def start_discussion(user_id: str, discussion_id: str, initial_question: str, client) -> Discussion:
    """
    Start a new discussion with initial question and draw tarot cards.
    This function creates a new discussion, draws cards, generates the initial response,
    and enhances it with feedback context from similar past readings.
    """
    logger.info(f"Starting new discussion for user {user_id}: {initial_question}")
    logger.debug(f"New discussion ID: {discussion_id}")
    
    deck = fetch_full_deck()
    if not deck:
        logger.error("Failed to fetch tarot deck")
        raise RuntimeError("Failed to fetch tarot deck")
    
    logger.info(f"Fetched deck with {len(deck)} cards")
    
    picks = layout_three_card(deck)
    logger.info(f"Drew {len(picks)} cards for reading")
    
    logger.debug(f"Cards drawn: {[card.name for card in picks]}")

    prompt = build_tarot_prompt(initial_question, picks)
    logger.debug(f"Generated prompt length: {len(prompt)} characters")
    
    base_response = call_gemini_api(prompt)
    logger.info(f"Generated base response length: {len(base_response) if base_response else 0} characters")
    
    if not base_response:
        base_response = "I apologize, but I was unable to generate a reading at this time. Please try again."
        logger.warning("Using fallback response due to empty base_response")
    
    try:
        logger.info("Attempting to enhance response with feedback context")
        
        # Enhance the response with context
        enhanced_result = enhance_reading_with_feedback_context(
            question=initial_question,
            cards= picks,
            base_interpretation=base_response
        )
        
        initial_response = enhanced_result.get("enhanced_interpretation", base_response)
        
        if "Context Enhancement" in initial_response:
            logger.info(f"Enhanced discussion response with feedback context for user {user_id}")
        else:
            logger.info("No context enhancement applied to response")
        
        contexts_count = enhanced_result.get("similar_contexts_count", 0)
        confidence_boost = enhanced_result.get("confidence_boost", 0)
        logger.info(f"Context enhancement - Similar contexts: {contexts_count}, Confidence boost: {confidence_boost}")
        
    except Exception as e:
        logger.warning(f"Could not enhance response with context: {e}")
        initial_response = base_response
    
    if not initial_response:
        initial_response = "I apologize, but I was unable to generate a reading at this time. Please try again."
    
    discussion = Discussion(
        discussion_id=discussion_id,
        user_id=user_id,
        created_at=datetime.now(),
        initial_question=initial_question,
        initial_response=initial_response,
        cards_drawn=picks
    )
    
    store_discussion(discussion, client)
    
    return discussion

def parse_cards_drawn(cards_drawn_str: str) -> List[CardLayout]:
    """
    Safely parse cards_drawn from Weaviate storage format.
    Handles JSON parsing errors, null values, and various data formats.
    """
    if not cards_drawn_str:
        return []
    
    cards_drawn = []
    try:
        cleaned_str = cards_drawn_str.replace("null", "null")  
        cards_data = json.loads(cleaned_str.replace("'", '"'))
        
        if isinstance(cards_data, list):
            cards_drawn = [CardLayout(**card_data) for card_data in cards_data if card_data is not None]
        else:
            print(f"Warning: cards_drawn is not a list: {type(cards_data)}")
            
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing cards_drawn as JSON: {e}")
        try:
            eval_str = cards_drawn_str.replace("null", "None")
            cards_data = ast.literal_eval(eval_str)  
            if isinstance(cards_data, list):
                cards_drawn = [CardLayout(**card_data) for card_data in cards_data if card_data is not None]
            else:
                print(f"Warning: eval result is not a list: {type(cards_data)}")
        except Exception as e2:
            print(f"Error with literal_eval fallback: {e2}")
            cards_drawn = []
    except Exception as e:
        print(f"Unexpected error parsing cards_drawn: {e}")
        cards_drawn = []
    
    return cards_drawn