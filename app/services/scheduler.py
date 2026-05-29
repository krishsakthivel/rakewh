# xgboost go brrr
import os
import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
from typing import List, Dict
from datetime import datetime

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../ml/recall_model.joblib")


def build_attempt_features(attempts: List[Dict], question: Dict, now: datetime) -> np.ndarray:
    q_attempts = [a for a in attempts if a["question_id"] == question["id"]]

    if not q_attempts:
        return np.array([
            0, 0.0, 0.0,
            question.get("difficulty", 0.5),
            999.0, 0.0, 0,
        ], dtype=np.float32)

    total = len(q_attempts)
    correct = sum(1 for a in q_attempts if a["correct"])
    accuracy = correct / total
    last_attempt = max(q_attempts, key=lambda a: a["attempted_at"])
    last_dt = last_attempt["attempted_at"]
    if isinstance(last_dt, str):
        last_dt = datetime.fromisoformat(last_dt)
    hours_since = (now - last_dt).total_seconds() / 3600.0
    avg_response_ms = np.mean([a.get("response_time_ms", 3000) or 3000 for a in q_attempts])
    last_correct = 1.0 if last_attempt["correct"] else 0.0

    return np.array([
        total, accuracy, last_correct,
        question.get("difficulty", 0.5),
        hours_since, avg_response_ms / 1000.0,
        1 if total > 0 and not last_attempt["correct"] else 0,
    ], dtype=np.float32)


def train_recall_model(training_rows: List[Dict]):
    if len(training_rows) < 20:
        return None

    df = pd.DataFrame(training_rows)
    X = df[["total_attempts", "accuracy", "last_correct", "difficulty",
            "hours_since", "avg_response_s", "last_wrong"]].values
    y = df["recalled_correctly"].values

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


def predict_recall_probability(model, features: np.ndarray) -> float:
    if model is None:
        hours = features[4]
        accuracy = features[1]
        decay = np.exp(-hours / 24.0)
        return float(accuracy * decay + 0.1)

    X = features.reshape(1, -1)
    prob = model.predict_proba(X)[0][1]
    return float(prob)


def select_questions_for_quiz(
    all_questions: List[Dict],
    attempts: List[Dict],
    current_module_id: int,
    n: int = 5,
) -> List[Dict]:
    now = datetime.utcnow()
    model = load_model()

    current_qs = [q for q in all_questions if q["module_id"] == current_module_id]
    prior_qs = [q for q in all_questions if q["module_id"] != current_module_id]

    scored_prior = []
    for q in prior_qs:
        features = build_attempt_features(attempts, q, now)
        recall_prob = predict_recall_probability(model, features)
        scored_prior.append((1.0 - recall_prob, q))

    scored_prior.sort(key=lambda x: x[0], reverse=True)

    n_current = max(3, int(n * 0.6))
    n_review = n - n_current

    combined = current_qs[:n_current] + [q for _, q in scored_prior[:n_review]]
    np.random.shuffle(combined)
    return combined


def get_mastery_scores(questions: List[Dict], attempts: List[Dict]) -> Dict[str, float]:
    concept_scores = {}
    for q in questions:
        tag = q.get("concept_tag", "unknown")
        q_attempts = [a for a in attempts if a["question_id"] == q["id"]]
        if not q_attempts:
            concept_scores.setdefault(tag, []).append(0.0)
        else:
            correct = sum(1 for a in q_attempts if a["correct"])
            concept_scores.setdefault(tag, []).append(correct / len(q_attempts))

    return {tag: float(np.mean(scores)) for tag, scores in concept_scores.items()}
