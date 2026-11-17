
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Pretrained multilingual NLI model
MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# Load the model only once
tokenizer = None
model = None


def load_model():
    """
    Load the pretrained NLI model and tokenizer.
    """

    global tokenizer, model

    if tokenizer is None or model is None:

        print("Loading multilingual NLI model...")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME
        )

        model.eval()

        print("NLI model loaded successfully!")


def get_label_name(label_id):
    """
    Convert the model's output label into a readable name.
    """

    label = model.config.id2label[label_id].lower()

    # Some models use generic labels such as LABEL_0
    if label.startswith("label_"):
        fallback_labels = {
            0: "contradiction",
            1: "entailment",
            2: "neutral"
        }

        return fallback_labels.get(label_id, "unknown")

    return label


def check_claim(claim, evidence_list):
    """
    Compare a claim against retrieved evidence.

    Returns:
        Supported
        Contradicted
        Insufficient Evidence
    """

    if not claim or not claim.strip():
        return {
            "result": "Insufficient Evidence",
            "confidence": 0.0,
            "evidence": None,
            "source": None
        }

    if not evidence_list:
        return {
            "result": "Insufficient Evidence",
            "confidence": 0.0,
            "evidence": None,
            "source": None
        }

    # Load the model
    load_model()

    best_prediction = None

    # Compare the claim with every retrieved evidence passage
    for item in evidence_list:

        evidence = item.get("evidence", "")

        if not evidence:
            continue

        # Evidence is the premise.
        # Claim is the hypothesis.
        inputs = tokenizer(
            evidence,
            claim,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():

            outputs = model(**inputs)

            probabilities = torch.softmax(
                outputs.logits,
                dim=1
            )[0]

        predicted_id = torch.argmax(probabilities).item()

        label = get_label_name(predicted_id)

        confidence = probabilities[predicted_id].item()

        prediction = {
            "label": label,
            "confidence": round(confidence * 100, 2),
            "evidence": evidence,
            "source": item.get("source"),
            "title": item.get("title")
        }

        # Keep the strongest prediction
        if (
            best_prediction is None
            or confidence > best_prediction["raw_confidence"]
        ):
            prediction["raw_confidence"] = confidence
            best_prediction = prediction

    if best_prediction is None:
        return {
            "result": "Insufficient Evidence",
            "confidence": 0.0,
            "evidence": None,
            "source": None
        }

    label = best_prediction["label"]
    confidence = best_prediction["confidence"]

    # Avoid making a decision when model confidence is low
    if confidence < 60:
        result = "Insufficient Evidence"

    elif label == "entailment":
        result = "Supported"

    elif label == "contradiction":
        result = "Contradicted"

    else:
        result = "Insufficient Evidence"

    return {
        "result": result,
        "confidence": confidence,
        "evidence": best_prediction["evidence"],
        "source": best_prediction["source"],
        "title": best_prediction["title"]
    }
