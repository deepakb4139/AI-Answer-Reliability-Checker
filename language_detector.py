
from langdetect import detect_langs, DetectorFactory, LangDetectException

# Ensure consistent language detection results
DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada"
}


def detect_language(text):
    """
    Detect the language of the given text.
    Supports English, Hindi and Kannada.
    """

    if not text or not text.strip():
        return {
            "language": "Unknown",
            "code": None,
            "confidence": 0.0,
            "supported": False
        }

    try:
        predictions = detect_langs(text)
        best_prediction = predictions[0]

        language_code = best_prediction.lang
        confidence = round(best_prediction.prob, 2)

        language_name = SUPPORTED_LANGUAGES.get(
            language_code, "Other Language"
        )

        return {
            "language": language_name,
            "code": language_code,
            "confidence": confidence,
            "supported": language_code in SUPPORTED_LANGUAGES
        }

    except LangDetectException:
        return {
            "language": "Unknown",
            "code": None,
            "confidence": 0.0,
            "supported": False
        }
