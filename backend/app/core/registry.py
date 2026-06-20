from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import Settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    _instance: Optional["ModelRegistry"] = None

    def __new__(cls) -> "ModelRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.loaded = False
            cls._instance.models = {}
            cls._instance.load_errors = {}
        return cls._instance

    def load_models(self, settings: Settings) -> None:
        if self.loaded:
            return
        assets = settings.assets_dir.resolve()
        self.models = {}
        self.load_errors = {}
        if not assets.exists():
            logger.warning("Assets directory does not exist: %s", assets)
            self.loaded = True
            return

        for path in assets.rglob("*"):
            if path.suffix.lower() not in {".pkl", ".joblib", ".index"}:
                continue
            key = self._asset_key(path)
            try:
                self.models[key] = self._load_asset(path)
                logger.info("Loaded asset %s from %s", key, path)
            except Exception as exc:
                self.load_errors[key] = str(exc)
                logger.warning("Failed loading asset %s from %s: %s", key, path, exc)

        self.closure_model = self.get_model("closure_prediction_model_v2")
        if self.closure_model is None:
            raise RuntimeError("Required closure model closure_prediction_model_v2 failed to load")
        logger.info("Loaded asset closure_prediction_model_v2")
        logger.info("Model class: %s", type(self.closure_model).__name__)
        self.encoders = self.get_model("closure_label_encoders", {})
        self.closure_metadata = self.get_model("closure_model_metadata_v2", {})
        self.corridor_priority = self.get_model("corridor_priority_lookup", {})
        self.zone_priority = self.get_model("zone_priority_lookup", {})
        self.retrieval_df = self.get_model("retrieval_df")
        self.retrieval_embeddings = self.get_model("retrieval_embeddings")
        self.retrieval_metadata = self.get_model("hybrid_retrieval_metadata", {})
        self.faiss_indexes = {key: value for key, value in self.models.items() if key.endswith("_index")}
        self.event_kb = self._load_pickle(assets / "knowledge_base" / "event_cause_knowledge_base.pkl", default={})
        if not self.event_kb:
            self.event_kb = self.get_model("event_cause_knowledge_base", {})
        self.loaded = True
        logger.info("Model registry initialized with %s assets and %s load errors", len(self.models), len(self.load_errors))

    def load(self, settings: Settings) -> None:
        self.load_models(settings)

    @staticmethod
    def _asset_key(path: Path) -> str:
        stem = path.stem.lower().replace(" ", "_").replace("(", "").replace(")", "")
        if path.suffix.lower() == ".index":
            return f"{stem}_index"
        return stem

    @staticmethod
    def _load_asset(path: Path) -> Any:
        if path.suffix.lower() == ".index":
            import faiss

            return faiss.read_index(str(path))
        if path.suffix.lower() in {".joblib", ".pkl"}:
            import joblib

            try:
                return joblib.load(path)
            except Exception as joblib_error:
                import pickle

                try:
                    with path.open("rb") as file:
                        return pickle.load(file)
                except Exception as pickle_error:
                    raise RuntimeError(f"joblib failed: {joblib_error}; pickle failed: {pickle_error}") from pickle_error
        raise ValueError(f"Unsupported asset type: {path.suffix}")

    @staticmethod
    def _load_pickle(path: Path, default: Any = None) -> Any:
        if not path.exists():
            return default
        try:
            return ModelRegistry._load_asset(path)
        except Exception:
            return default

    def get_model(self, name: str, default: Any = None) -> Any:
        return self.models.get(name.lower(), default)

    def list_models(self) -> Dict[str, str]:
        return {key: type(value).__name__ for key, value in self.models.items()}

    def health_check(self) -> dict:
        return {
            "loaded": self.loaded,
            "asset_count": len(self.models),
            "load_error_count": len(self.load_errors),
            "load_errors": self.load_errors,
        }


model_registry = ModelRegistry()
print(model_registry.list_models())
#print(type(model_registry.faiss_indexes["unplanned_accident_index"]))