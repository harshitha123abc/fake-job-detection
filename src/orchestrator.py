"""
LangGraph Orchestration for Multi-Agent Fake Job Detection
Controls execution order, passes data between agents, handles multi-step reasoning
"""

from langgraph.graph import StateGraph, END
from typing import Dict, TypedDict, Optional, List
from src.agent import (
    JobExtractorAgent,
    CrossPlatformSearchAgent,
    CompanyVerificationAgent,
    ScamDetectionAgent,
    DecisionAgent
)
from src.model import FakeJobDetectionModel


class PipelineState(TypedDict):
    """State object that flows through the LangGraph pipeline"""
    job_text: str
    
    # Extractor outputs
    extracted_info: Dict
    extraction_confidence: float
    
    # Search outputs
    search_results: Dict
    platform_found: bool
    
    # Verification outputs
    verification_results: Dict
    company_verified: bool
    
    # Scam detection outputs
    scam_indicators: Dict
    scam_score: float
    
    # ML model outputs
    ml_result: Dict
    ml_fake_probability: float
    
    # Final decision
    final_result: Optional[Dict]
    error: Optional[str]


class FakeJobDetectorOrchestrator:
    """
    LangGraph-based orchestrator for fake job detection.
    Manages state, execution order, error handling, and conditional routing.
    """
    
    def __init__(self):
        self.extractor = JobExtractorAgent()
        self.search_agent = CrossPlatformSearchAgent()
        self.verification_agent = CompanyVerificationAgent()
        self.scam_detector = ScamDetectionAgent()
        self.decision_agent = DecisionAgent()
        self.ml_model = FakeJobDetectionModel()

        try:
            self.ml_model.load()
        except Exception:
            self.ml_model = None
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph state machine"""
        workflow = StateGraph(PipelineState)
        
        # Add nodes (agents)
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("search", self._search_node)
        workflow.add_node("verify", self._verify_node)
        workflow.add_node("scam_detect", self._scam_detect_node)
        workflow.add_node("ml_predict", self._ml_node)
        workflow.add_node("decide", self._decide_node)
        
        # Add edges (connections between agents)
        workflow.add_edge("extract", "search")
        workflow.add_edge("search", "verify")
        workflow.add_edge("verify", "scam_detect")
        workflow.add_edge("scam_detect", "ml_predict")
        workflow.add_edge("ml_predict", "decide")
        workflow.add_edge("decide", END)
        
        # Set entry point
        workflow.set_entry_point("extract")
        
        return workflow.compile()
    
    def _extract_node(self, state: PipelineState) -> PipelineState:
        """Node 1: Extract job information"""
        try:
            result = self.extractor.extract(state["job_text"])
            state["extracted_info"] = result
            state["extraction_confidence"] = result.get("extraction_confidence", 0)
        except Exception as e:
            state["error"] = f"Extraction error: {str(e)}"
        
        return state
    
    def _search_node(self, state: PipelineState) -> PipelineState:
        """Node 2: Cross-platform search"""
        try:
            if state.get("error"):
                return state
            
            search_result = self.search_agent.search(
                state["extracted_info"].get("company", ""),
                state["extracted_info"].get("role", ""),
                raw_text=state["job_text"]
            )
            state["search_results"] = search_result
            state["platform_found"] = search_result.get("platform_found", False)
        except Exception as e:
            state["error"] = f"Search error: {str(e)}"
        
        return state
    
    def _verify_node(self, state: PipelineState) -> PipelineState:
        """Node 3: Company verification"""
        try:
            if state.get("error"):
                return state
            
            verification_result = self.verification_agent.verify(
                state["extracted_info"].get("company", ""),
                raw_text=state["job_text"]
            )
            state["verification_results"] = verification_result
            state["company_verified"] = verification_result.get("verification_score", 0) >= 0.5
        except Exception as e:
            state["error"] = f"Verification error: {str(e)}"
        
        return state
    
    def _scam_detect_node(self, state: PipelineState) -> PipelineState:
        """Node 4: Scam detection"""
        try:
            if state.get("error"):
                return state
            
            scam_result = self.scam_detector.detect_scams(state["job_text"])
            state["scam_indicators"] = scam_result
            state["scam_score"] = scam_result.get("scam_score", 0)
        except Exception as e:
            state["error"] = f"Scam detection error: {str(e)}"
        
        return state
    
    def _ml_node(self, state: PipelineState) -> PipelineState:
        """Node 5: ML prediction using TF-IDF + Logistic Regression"""
        try:
            if state.get("error"):
                return state

            if self.ml_model is None:
                state["ml_result"] = {
                    "ml_available": False,
                    "ml_fake_probability": 0.0,
                    "explanation": "ML model not available."
                }
                state["ml_fake_probability"] = 0.0
                return state

            ml_proba = self.ml_model.predict_proba([state["job_text"]])[0]
            fake_probability = float(ml_proba[1]) if len(ml_proba) > 1 else 0.0
            ml_prediction, ml_confidence = self.ml_model.predict(state["job_text"])

            state["ml_result"] = {
                "ml_available": True,
                "ml_prediction": ml_prediction,
                "ml_fake_probability": fake_probability,
                "ml_confidence": float(ml_confidence),
                "ml_risk_score": round(fake_probability * 100, 1),
                "explanation": "ML-based scam probability from TF-IDF + Logistic Regression"
            }
            state["ml_fake_probability"] = fake_probability
        except Exception as e:
            state["ml_result"] = {
                "ml_available": False,
                "ml_fake_probability": 0.0,
                "explanation": f"ML prediction failed: {str(e)}"
            }
            state["ml_fake_probability"] = 0.0
        
        return state

    def _decide_node(self, state: PipelineState) -> PipelineState:
        """Node 6: Final decision from aggregated data"""
        try:
            if state.get("error"):
                return state
            
            final_result = self.decision_agent.decide(
                state["extracted_info"],
                state["search_results"],
                state["verification_results"],
                state["scam_indicators"],
                state.get("ml_result", {})
            )
            state["final_result"] = final_result
        except Exception as e:
            state["error"] = f"Decision error: {str(e)}"
        
        return state
    
    def detect(self, job_text: str) -> Dict:
        """Run the complete orchestrated pipeline"""
        initial_state: PipelineState = {
            "job_text": job_text,
            "extracted_info": {},
            "extraction_confidence": 0,
            "search_results": {},
            "platform_found": False,
            "verification_results": {},
            "company_verified": False,
            "scam_indicators": {},
            "scam_score": 0,
            "ml_result": {},
            "ml_fake_probability": 0.0,
            "final_result": None,
            "error": None
        }
        
        # Execute the graph
        result_state = self.graph.invoke(initial_state)
        
        # Handle errors
        if result_state.get("error"):
            return {
                "error": result_state["error"],
                "risk_level": "Unknown",
                "final_risk_score": 0
            }
        
        # Return the final result with additional pipeline metadata
        final_result = result_state["final_result"]
        final_result["_pipeline_metadata"] = {
            "extraction_confidence": result_state["extraction_confidence"],
            "platform_found": result_state["platform_found"],
            "company_verified": result_state["company_verified"],
            "scam_score": result_state["scam_score"],
            "ml_fake_probability": result_state.get("ml_fake_probability", 0),
            "ml_available": result_state.get("ml_result", {}).get("ml_available", False)
        }
        
        return final_result
