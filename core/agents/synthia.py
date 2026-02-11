"""
Synthia Agent - Synthesis and Creative Operations Core

The Synthia agent is responsible for content synthesis, creative problem solving,
natural language processing, and user interaction within the ARCHONX dual-crew system.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class SynthiaAgent:
    """
    Core synthesis and creative agent for the ARCHONX operating system.
    
    Responsibilities:
    - Content synthesis and generation
    - Creative problem solving
    - Natural language processing
    - User interaction and communication
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Synthia agent.
        
        Args:
            config: Configuration dictionary for agent initialization
        """
        self.config = config or {}
        self.agent_id = "synthia"
        self.agent_type = "creative"
        self.status = "initialized"
        self.logger = self._setup_logger()
        self.metrics = {
            "tasks_completed": 0,
            "content_generated": 0,
            "interactions_handled": 0,
            "problems_solved": 0
        }
        
        self.logger.info(f"Synthia agent initialized with config: {self.config}")
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger(f"archonx.{self.agent_id}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def synthesize_content(self, inputs: List[str], style: str = "informative") -> Dict[str, Any]:
        """
        Synthesize content from multiple inputs.
        
        Args:
            inputs: List of input strings to synthesize
            style: Desired output style
            
        Returns:
            Synthesized content dictionary
        """
        self.logger.info(f"Synthesizing content from {len(inputs)} inputs with style: {style}")
        
        # Simple synthesis: combine and format inputs
        synthesized = self._combine_inputs(inputs, style)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "input_count": len(inputs),
            "style": style,
            "content": synthesized,
            "metadata": {
                "word_count": len(synthesized.split()),
                "character_count": len(synthesized)
            }
        }
        
        self.metrics["content_generated"] += 1
        self.metrics["tasks_completed"] += 1
        
        return result
    
    def _combine_inputs(self, inputs: List[str], style: str) -> str:
        """Combine inputs based on style."""
        if not inputs:
            return ""
        
        if style == "informative":
            return " ".join(inputs)
        elif style == "creative":
            return " ~ ".join(inputs) + " ~"
        elif style == "technical":
            return "\n".join(f"- {inp}" for inp in inputs)
        else:
            return " ".join(inputs)
    
    def solve_problem(self, problem: str, constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Apply creative problem solving.
        
        Args:
            problem: Problem description
            constraints: Optional list of constraints
            
        Returns:
            Solution dictionary
        """
        self.logger.info(f"Solving problem: {problem}")
        
        constraints = constraints or []
        
        # Generate creative approaches
        approaches = self._generate_approaches(problem, constraints)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "problem": problem,
            "constraints": constraints,
            "approaches": approaches,
            "recommended_approach": approaches[0] if approaches else None
        }
        
        self.metrics["problems_solved"] += 1
        self.metrics["tasks_completed"] += 1
        
        return result
    
    def _generate_approaches(self, problem: str, constraints: List[str]) -> List[Dict[str, str]]:
        """Generate creative approaches to problem."""
        approaches = [
            {
                "name": "Analytical Approach",
                "description": "Break down the problem into smaller components and analyze each part systematically.",
                "feasibility": "high"
            },
            {
                "name": "Collaborative Approach",
                "description": "Engage multiple agents to contribute different perspectives and expertise.",
                "feasibility": "high"
            },
            {
                "name": "Iterative Approach",
                "description": "Develop solution incrementally with feedback loops at each stage.",
                "feasibility": "medium"
            }
        ]
        
        # Filter based on constraints
        if "time_critical" in constraints:
            approaches[0]["priority"] = "high"
        
        return approaches
    
    def process_natural_language(self, text: str) -> Dict[str, Any]:
        """
        Process natural language input.
        
        Args:
            text: Input text to process
            
        Returns:
            Processing result
        """
        self.logger.info(f"Processing natural language: {text[:50]}...")
        
        # Simple NLP processing
        tokens = text.split()
        sentences = text.split('.')
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "original_text": text,
            "tokens": tokens,
            "token_count": len(tokens),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "sentiment": self._analyze_sentiment(text),
            "key_phrases": self._extract_key_phrases(tokens)
        }
        
        self.metrics["tasks_completed"] += 1
        
        return result
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'happy', 'positive', 'success']
        negative_words = ['bad', 'poor', 'terrible', 'sad', 'negative', 'failure']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_key_phrases(self, tokens: List[str]) -> List[str]:
        """Extract key phrases from tokens."""
        # Simple approach: return longer words as key phrases
        key_phrases = [token for token in tokens if len(token) > 5]
        return key_phrases[:5]  # Return top 5
    
    def handle_interaction(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle user interaction.
        
        Args:
            user_input: User's input text
            context: Optional context dictionary
            
        Returns:
            Interaction response
        """
        self.logger.info(f"Handling user interaction: {user_input[:50]}...")
        
        context = context or {}
        
        # Process the input
        nlp_result = self.process_natural_language(user_input)
        
        # Generate response
        response = self._generate_response(user_input, nlp_result, context)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "user_input": user_input,
            "response": response,
            "context": context,
            "nlp_analysis": {
                "sentiment": nlp_result["sentiment"],
                "token_count": nlp_result["token_count"]
            }
        }
        
        self.metrics["interactions_handled"] += 1
        self.metrics["tasks_completed"] += 1
        
        return result
    
    def _generate_response(self, user_input: str, nlp_result: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate appropriate response to user input."""
        sentiment = nlp_result["sentiment"]
        
        if "help" in user_input.lower():
            return "I'm Synthia, here to assist you with creative solutions and natural language processing. How can I help?"
        elif "status" in user_input.lower():
            return f"I'm operating normally. I've handled {self.metrics['interactions_handled']} interactions so far."
        elif sentiment == "positive":
            return "I'm glad to hear that! How can I assist you further?"
        elif sentiment == "negative":
            return "I understand your concern. Let me help you find a solution."
        else:
            return "I'm processing your request. Could you provide more details?"
    
    def generate_content(self, topic: str, length: str = "medium", format_type: str = "text") -> Dict[str, Any]:
        """
        Generate content on a given topic.
        
        Args:
            topic: Topic to generate content about
            length: Desired length (short, medium, long)
            format_type: Output format (text, list, structured)
            
        Returns:
            Generated content
        """
        self.logger.info(f"Generating {length} {format_type} content on: {topic}")
        
        content = self._create_content(topic, length, format_type)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "topic": topic,
            "length": length,
            "format": format_type,
            "content": content
        }
        
        self.metrics["content_generated"] += 1
        self.metrics["tasks_completed"] += 1
        
        return result
    
    def _create_content(self, topic: str, length: str, format_type: str) -> Any:
        """Create content based on parameters."""
        if format_type == "list":
            items = [
                f"Key aspect of {topic}: item 1",
                f"Important consideration for {topic}",
                f"Advanced concept in {topic}"
            ]
            if length == "long":
                items.extend([
                    f"Additional detail about {topic}",
                    f"Expert insight on {topic}"
                ])
            return items
        elif format_type == "structured":
            return {
                "title": f"Overview of {topic}",
                "introduction": f"This content covers {topic} in detail.",
                "key_points": [
                    f"Point 1 about {topic}",
                    f"Point 2 about {topic}"
                ]
            }
        else:  # text format
            if length == "short":
                return f"Brief overview of {topic}."
            elif length == "long":
                return f"Comprehensive exploration of {topic}, covering multiple aspects and perspectives. This includes detailed analysis and practical applications."
            else:  # medium
                return f"This content explores {topic}, providing insights and practical information."
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "metrics": self.metrics.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Gracefully shutdown the agent."""
        self.logger.info("Shutting down Synthia agent")
        self.status = "shutdown"


def main():
    """Main entry point for Synthia agent."""
    print("Initializing Synthia Agent...")
    
    # Create agent instance
    agent = SynthiaAgent()
    
    # Demo operations
    print("\n=== Synthia Agent Demo ===")
    
    # Content synthesis
    synthesis = agent.synthesize_content(
        ["Machine learning", "Natural language processing", "Computer vision"],
        style="technical"
    )
    print(f"\nContent Synthesis:\n{json.dumps(synthesis, indent=2)}")
    
    # Problem solving
    solution = agent.solve_problem(
        "How to improve system performance",
        constraints=["time_critical", "resource_limited"]
    )
    print(f"\nProblem Solving:\n{json.dumps(solution, indent=2)}")
    
    # User interaction
    interaction = agent.handle_interaction("Hello, I need help with the system")
    print(f"\nUser Interaction:\n{json.dumps(interaction, indent=2)}")
    
    # Content generation
    content = agent.generate_content("artificial intelligence", length="medium", format_type="list")
    print(f"\nContent Generation:\n{json.dumps(content, indent=2)}")
    
    # Status
    status = agent.get_status()
    print(f"\nAgent Status:\n{json.dumps(status, indent=2)}")
    
    agent.shutdown()
    print("\nSynthia Agent demonstration complete.")


if __name__ == "__main__":
    main()
