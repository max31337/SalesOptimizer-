from datetime import timedelta
from typing import List, Dict
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sqlalchemy.orm import Session
from app.models import Opportunity, Interaction, OpportunityStage

class OpportunityModelEngine:
    def __init__(self, db: Session):
        self.db = db
        self.min_customer_opportunities = 10
        self.prob_model = None
        self.date_model = None
        self.confidence_model = None
        self.stage_mapping = {
            OpportunityStage.LEAD.value: 0,
            OpportunityStage.PROSPECT.value: 1,
            OpportunityStage.NEGOTIATION.value: 2,
            OpportunityStage.CLOSED_WON.value: 3,
            OpportunityStage.CLOSED_LOST.value: 4
        }

    def _extract_interaction_features(self, opportunity: Opportunity) -> Dict:
        """
        Extract features from interaction data for the given opportunity.
        """
        now = opportunity.created_at
        interactions = self.db.query(Interaction).filter(
            Interaction.customer_id == opportunity.customer_id,
            Interaction.interaction_date <= now
        ).all()

        if not interactions:
            return {
                'interaction_count_last_30_days': 0,
                'days_since_last_interaction': 999,
                'num_follow_ups_scheduled': 0,
                'num_meetings_or_calls': 0,
                'last_follow_up_status_pending': 0,
                'last_follow_up_status_done': 0,
                'last_follow_up_status_cancelled': 0,
            }

        last_30_days = [i for i in interactions if (now - i.interaction_date).days <= 30]
        follow_ups = [i for i in interactions if i.follow_up_date and i.follow_up_date > now]
        meetings_or_calls = [i for i in interactions if i.type in ('MEETING', 'CALL')]

        # Handle latest follow_up_status
        interactions_sorted = sorted(interactions, key=lambda i: i.interaction_date, reverse=True)
        latest_status = interactions_sorted[0].follow_up_status or ""
        status_flags = {
            'last_follow_up_status_pending': int(latest_status == 'PENDING'),
            'last_follow_up_status_done': int(latest_status == 'DONE'),
            'last_follow_up_status_cancelled': int(latest_status == 'CANCELLED'),
        }

        return {
            'interaction_count_last_30_days': len(last_30_days),
            'days_since_last_interaction': (now - interactions_sorted[0].interaction_date).days,
            'num_follow_ups_scheduled': len(follow_ups),
            'num_meetings_or_calls': len(meetings_or_calls),
            **status_flags
        }

    def _prepare_features(self, opportunities: List[Opportunity]) -> pd.DataFrame:
        features = []
        for opp in opportunities:
            feature_dict = {
                'deal_value': opp.deal_value,
                'stage': self.stage_mapping.get(opp.stage, 0),
                'initial_probability': opp.probability,
                'days_to_expected_close': (opp.expected_close_date - opp.created_at).days,
                'customer_revenue': opp.customer.annual_revenue if opp.customer else 0,
                'customer_employees': opp.customer.employee_count if opp.customer else 0
            }

            interaction_features = self._extract_interaction_features(opp)
            feature_dict.update(interaction_features)
            features.append(feature_dict)

        # Debug: log the features for the opportunity being predicted
        print(f"Prepared features for opportunity {opp.id}: {feature_dict}")
        
        return pd.DataFrame(features)

    def train(self, opportunities: List[Opportunity]):
        """
        Train models and store them for later use in predictions.
        """
        prob_model, date_model, confidence_model = self._train_models(opportunities)
        self.prob_model = prob_model
        self.date_model = date_model
        self.confidence_model = confidence_model

    def _train_models(self, opportunities: List[Opportunity]):
        """
        Train the prediction models (probability, close date, and confidence).
        """
        valid_opps = [opp for opp in opportunities if opp.closed_date and opp.created_at]
        X = self._prepare_features(valid_opps)
        y_prob = np.array([1 if opp.stage.value == 'CLOSED_WON' else 0 for opp in valid_opps])
        y_date = np.array([(opp.closed_date - opp.created_at).days for opp in valid_opps])

        # Training the models
        prob_model = RandomForestClassifier(n_estimators=100)
        prob_model.fit(X, y_prob)

        date_model = RandomForestRegressor(n_estimators=100)
        date_model.fit(X, y_date)

        confidence_model = RandomForestRegressor(n_estimators=100)

        return prob_model, date_model, confidence_model


    def predict(self, opportunity: Opportunity) -> Dict:
        # Special handling for already closed opportunities
        if opportunity.stage.value == OpportunityStage.CLOSED_WON.value:
            return {
                "predicted_probability": 1.0,
                "predicted_close_date": opportunity.closed_date or opportunity.created_at,
                "confidence_score": 1.0,
                "risk_factors": "No risk factors, deal closed successfully"
            }
        elif opportunity.stage.value == OpportunityStage.CLOSED_LOST.value:
            return {
                "predicted_probability": 0.0,
                "predicted_close_date": opportunity.closed_date or opportunity.created_at,
                "confidence_score": 1.0,
                "risk_factors": "Deal already closed as lost"
            }

        # Ensure that models are trained before prediction
        if not self.prob_model or not self.date_model:
            # If models are not trained, raise an exception or handle the case
            raise ValueError("Models are not trained yet")

        # Prepare features for prediction
        X = self._prepare_features([opportunity])

        # Prediction
        proba = self.prob_model.predict_proba(X)[0]
        prob_pred = proba[1] if len(proba) > 1 else proba[0]
        days_to_close = self.date_model.predict(X)[0]

        # Debug: Print predicted probability and confidence score
        print(f"Predicted probability: {prob_pred}")

        # Confidence score should be highest at 0 and 1, lowest at 0.5
        confidence_score = 1.0 - 2 * min(prob_pred, 1 - prob_pred)
        print(f"Confidence score: {confidence_score}")

        # Determine risk factors based on the probability
        risk_factors = []
        if prob_pred < 0.3:
            risk_factors.append("Low win probability")
        if days_to_close > 90:
            risk_factors.append("Long sales cycle predicted")
        if confidence_score < 0.4:
            risk_factors.append("High prediction uncertainty")

        # Return results
        return {
            "predicted_probability": float(prob_pred),
            "predicted_close_date": opportunity.created_at + timedelta(days=int(days_to_close)),
            "confidence_score": float(confidence_score),
            "risk_factors": ", ".join(risk_factors) if risk_factors else "No significant risks identified"
        }