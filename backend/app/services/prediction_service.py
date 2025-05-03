from sqlalchemy.orm import Session
from typing import Dict, List
from app.models import Opportunity
from app.ml.opportunity_model import OpportunityModelEngine

class OpportunityPredictionService:
    def __init__(self, db: Session, training_data: List[Opportunity] = None):
        self.engine = OpportunityModelEngine(db)
        
        # Train the model if training data is provided
        if training_data:
            self.train_models(training_data)
    
    def train_models(self, opportunities: List[Opportunity]):
        """
        Train the models with the provided opportunities data.
        """
        self.engine.train(opportunities)
    
    def predict_opportunity(self, opportunity: Opportunity) -> Dict:
        # Ensure the models are trained before predicting
        if not self.engine.prob_model or not self.engine.date_model:
            raise ValueError("Models are not trained yet")
        
        return self.engine.predict(opportunity)
