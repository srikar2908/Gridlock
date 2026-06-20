from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from app.core.logger import get_logger
from app.core.registry import ModelRegistry
from app.schemas.requests import IncidentRequest
from app.schemas.responses import ClosurePrediction

logger = get_logger(__name__)


class ClosureService:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def predict(self, incident: IncidentRequest) -> ClosurePrediction:
        model = getattr(self.registry, "closure_model", None)
        if model is None or not hasattr(model, "predict_proba"):
            raise RuntimeError("Closure model is not loaded")
        try:
            details = self.debug_prediction(incident)
            probability = float(details["final_probability"])
            threshold = float(self.registry.closure_metadata.get("best_threshold", 0.5))
            return ClosurePrediction(
                closure_required=probability >= threshold,
                confidence=round(probability, 3),
                model_version=self.registry.closure_metadata.get("model_name", "closure_prediction_model_v2"),
            )
        except Exception as e:
            logger.exception(
                "Closure prediction failed",
                extra={"error": str(e), "event_type": incident.event_type, "corridor": incident.corridor},
            )
            raise

    def debug_prediction(self, incident: IncidentRequest) -> dict:
        model = getattr(self.registry, "closure_model", None)
        if model is None or not hasattr(model, "predict_proba"):
            raise RuntimeError("Closure model is not loaded")

        raw_features = self._build_raw_features(incident)
        features = self._encode_features(raw_features)
        probabilities = model.predict_proba(features)[0]
        class_labels = [self._json_value(item) for item in getattr(model, "classes_", [])]
        positive_index = self._positive_class_index(class_labels)
        positive_probability = float(probabilities[positive_index])
        threshold = float(self.registry.closure_metadata.get("best_threshold", 0.5))
        final_probability, calibration = self._apply_operational_calibration(
            probability=positive_probability,
            incident=incident,
            raw_features=raw_features,
        )
        predicted_index = int(np.argmax(probabilities))
        final_class = 1 if final_probability >= threshold else 0

        debug = {
            "model_class": model.__class__.__name__,
            "model_version": self.registry.closure_metadata.get("model_name", "closure_prediction_model_v2"),
            "expected_model_features": list(features.columns),
            "raw_features": raw_features,
            "encoded_features": features.iloc[0].to_dict(),
            "probabilities": {
                str(class_labels[index] if index < len(class_labels) else index): float(value)
                for index, value in enumerate(probabilities)
            },
            "probability_vector": [float(value) for value in probabilities],
            "class_labels": class_labels,
            "positive_class": class_labels[positive_index] if positive_index < len(class_labels) else positive_index,
            "positive_class_index": positive_index,
            "positive_probability": positive_probability,
            "threshold": threshold,
            "raw_predicted_class": class_labels[predicted_index] if predicted_index < len(class_labels) else predicted_index,
            "predicted_class": final_class,
            "final_probability": final_probability,
            "closure_required": final_probability >= threshold,
            "calibration": calibration,
        }
        logger.debug("Closure debug payload: %s", debug)
        return debug

    def _build_features(self, incident: IncidentRequest) -> pd.DataFrame:
        return self._encode_features(self._build_raw_features(incident))

    def _build_raw_features(self, incident: IncidentRequest) -> dict:
        metadata = incident.metadata or {}
        now = datetime.utcnow()
        event_type = str(metadata.get("event_category") or metadata.get("event_type") or "unplanned")
        event_cause = incident.event_type.strip().lower().replace(" ", "_")
        description = incident.description or ""
        junction = str(metadata.get("junction") or self._infer_junction(description) or "nan")
        veh_type = str(metadata.get("veh_type") or self._infer_vehicle_type(incident, description) or "nan")
        zone = self._normalize_category("zone", incident.zone)
        base = {
            "event_type": event_type,
            "event_cause": event_cause,
            "corridor": incident.corridor,
            "junction": junction,
            "zone": zone,
            "police_station": str(metadata.get("police_station") or "nan"),
            "veh_type": veh_type,
            "hour": int(metadata.get("hour") or now.hour),
            "weekday": int(metadata.get("weekday") or now.weekday()),
            "month": int(metadata.get("month") or now.month),
            "is_weekend": int(now.weekday() >= 5),
            "is_peak": int(now.hour in {8, 9, 10, 17, 18, 19, 20}),
            "latitude": float(metadata.get("latitude") or 0.0),
            "longitude": float(metadata.get("longitude") or 0.0),
        }

        df = self._historical_frame()
        base["corridor_event_count"] = self._count(df, "corridor", incident.corridor)
        base["junction_event_count"] = 0 if base["junction"] == "nan" else self._count(df, "junction", base["junction"])
        for column, source_value in {
            "event_type_closure_rate": ("event_type", event_type),
            "event_cause_closure_rate": ("event_cause", event_cause),
            "corridor_closure_rate": ("corridor", incident.corridor),
            "junction_closure_rate": ("junction", base["junction"]),
            "zone_closure_rate": ("zone", incident.zone),
            "police_station_closure_rate": ("police_station", base["police_station"]),
            "veh_type_closure_rate": ("veh_type", base["veh_type"]),
        }.items():
            base[column] = self._closure_rate(df, source_value[0], source_value[1])
        return base

    def _encode_features(self, base: dict) -> pd.DataFrame:
        features = self.registry.closure_metadata.get("features") or list(getattr(self.registry.closure_model, "feature_names_in_", []))
        encoded = {}
        for feature in features:
            value = base.get(feature, 0)
            if feature in getattr(self.registry, "encoders", {}):
                value = self._encode(feature, str(value))
            encoded[feature] = value
        return pd.DataFrame([encoded], columns=features)

    def _historical_frame(self):
        df = getattr(self.registry, "retrieval_df", None)
        return df if hasattr(df, "columns") else None

    @staticmethod
    def _count(df: Any, column: str, value: str) -> int:
        if df is None or column not in df.columns:
            return 0
        return int((df[column].astype(str) == str(value)).sum())

    @staticmethod
    def _closure_rate(df: Any, column: str, value: str) -> float:
        if df is None or column not in df.columns or "requires_road_closure" not in df.columns:
            return 0.0
        subset = df[df[column].astype(str) == str(value)]
        if subset.empty:
            return 0.0
        closure = subset["requires_road_closure"].astype(str).str.lower().isin({"true", "1", "yes"})
        return float(closure.mean())

    def _encode(self, feature: str, value: str) -> int:
        encoder = self.registry.encoders[feature]
        classes = [str(item) for item in encoder.classes_]
        if value in classes:
            return int(encoder.transform([value])[0])
        if "nan" in classes:
            return int(encoder.transform(["nan"])[0])
        return int(encoder.transform([encoder.classes_[0]])[0])

    def _normalize_category(self, feature: str, value: str) -> str:
        encoder = getattr(self.registry, "encoders", {}).get(feature)
        if encoder is None:
            return value
        candidates = [str(item) for item in encoder.classes_]
        lowered = str(value).strip().lower()
        for candidate in candidates:
            if candidate.lower() == lowered:
                return candidate
        for candidate in candidates:
            if candidate.lower().startswith(lowered):
                return candidate
        return value

    @staticmethod
    def _infer_vehicle_type(incident: IncidentRequest, description: str) -> str | None:
        text = f"{incident.event_type} {description}".lower()
        if any(term in text for term in ["tanker", "truck", "lorry"]):
            return "truck"
        if "bus" in text:
            return "bmtc_bus"
        if any(term in text for term in ["car", "cab", "taxi"]):
            return "private_car"
        if "auto" in text:
            return "auto"
        if "lcv" in text:
            return "lcv"
        return None

    @staticmethod
    def _infer_junction(description: str) -> str | None:
        text = description.lower()
        if "junction" in text or "jn" in text or "circle" in text:
            return "nan"
        return None

    @staticmethod
    def _positive_class_index(class_labels: list[Any]) -> int:
        for index, label in enumerate(class_labels):
            if label is True or str(label).strip().lower() in {"1", "true", "yes", "closure", "closed", "required"}:
                return index
        return len(class_labels) - 1 if class_labels else 1

    @staticmethod
    def _json_value(value: Any) -> Any:
        if hasattr(value, "item"):
            return value.item()
        return value

    @staticmethod
    def _apply_operational_calibration(probability: float, incident: IncidentRequest, raw_features: dict) -> tuple[float, dict]:
        text = f"{incident.event_type} {incident.description}".lower()
        severity = (incident.severity or "").lower()
        high_risk_event = any(term in text for term in ["accident", "collision", "crash"])
        hazardous_vehicle = any(term in text for term in ["tanker", "fuel", "hazmat", "chemical", "truck"])
        severe_impact = any(term in text for term in ["severe congestion", "blocked", "major junction", "junction"])
        critical = severity == "critical"
        if critical and high_risk_event and (hazardous_vehicle or severe_impact):
            floor = 0.72
            return max(probability, floor), {
                "applied": probability < floor,
                "type": "critical_hazardous_collision_operational_floor",
                "model_probability": probability,
                "floor": floor,
                "signals": {
                    "critical": critical,
                    "high_risk_event": high_risk_event,
                    "hazardous_vehicle": hazardous_vehicle,
                    "severe_impact": severe_impact,
                    "encoded_vehicle_type": raw_features.get("veh_type"),
                },
            }
        return probability, {"applied": False, "model_probability": probability}
