"""
Configuration Management for RAG System
Loads settings from environment variables and provides structured access.
"""

import os
from pathlib import Path
from typing import Optional, Literal
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    supabase_url: str
    supabase_service_key: str
    supabase_anon_key: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    pool_size: int = 10
    max_overflow: int = 20
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", ""),
            supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", ""),
            db_host=os.getenv("DB_HOST", ""),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "postgres"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", ""),
            pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20"))
        )
    
    def validate(self) -> bool:
        """Validate that required fields are set"""
        required = [self.supabase_url, self.supabase_service_key, self.db_password]
        return all(required)


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    provider: Literal["openai", "anthropic"]
    openai_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    openai_model: str
    anthropic_model: str
    max_context_length: int = 8000
    temperature: float = 0.1
    
    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            provider=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5.1"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            max_context_length=int(os.getenv("MAX_CONTEXT_LENGTH", "8000"))
        )
    
    def get_api_key(self) -> str:
        """Get API key for configured provider"""
        if self.provider == "openai":
            return self.openai_api_key or ""
        else:
            return self.anthropic_api_key or ""
    
    def get_model(self) -> str:
        """Get model name for configured provider"""
        if self.provider == "openai":
            return self.openai_model
        else:
            return self.anthropic_model


@dataclass
class EmbeddingConfig:
    """Embedding model configuration"""
    model_name: str
    dimension: int
    batch_size: int
    cache_dir: Optional[str]
    use_gpu: bool = False
    
    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        return cls(
            model_name=os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"),
            dimension=int(os.getenv("EMBEDDING_DIMENSION", "384")),
            batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
            cache_dir=os.getenv("TRANSFORMERS_CACHE"),
            use_gpu=os.getenv("USE_GPU", "false").lower() == "true"
        )


@dataclass
class PathConfig:
    """File path configuration"""
    json_folder: Path
    output_folder: Path
    logs_folder: Path
    
    @classmethod
    def from_env(cls) -> "PathConfig":
        config = cls(
            json_folder=Path(os.getenv("JSON_FOLDER_PATH", "./parsed_10k_json")),
            output_folder=Path(os.getenv("OUTPUT_FOLDER", "./output")),
            logs_folder=Path(os.getenv("LOGS_FOLDER", "./logs"))
        )
        # Create directories if they don't exist
        config.output_folder.mkdir(parents=True, exist_ok=True)
        config.logs_folder.mkdir(parents=True, exist_ok=True)
        return config


@dataclass
class ProcessingConfig:
    """Processing parameters"""
    db_batch_size: int
    default_top_k: int
    similarity_threshold: float
    num_workers: int
    
    @classmethod
    def from_env(cls) -> "ProcessingConfig":
        return cls(
            db_batch_size=int(os.getenv("DB_BATCH_SIZE", "500")),
            default_top_k=int(os.getenv("DEFAULT_TOP_K", "5")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.3")),
            num_workers=int(os.getenv("NUM_WORKERS", "4"))
        )


@dataclass
class CacheConfig:
    """Query cache configuration"""
    enabled: bool
    ttl_hours: int
    max_size: int
    
    @classmethod
    def from_env(cls) -> "CacheConfig":
        return cls(
            enabled=os.getenv("ENABLE_QUERY_CACHE", "true").lower() == "true",
            ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "24")),
            max_size=int(os.getenv("MAX_CACHE_SIZE", "1000"))
        )


@dataclass
class FeatureFlags:
    """Feature toggles"""
    hybrid_search: bool
    full_text_search: bool
    context_expansion: bool
    query_rewriting: bool
    response_streaming: bool
    
    @classmethod
    def from_env(cls) -> "FeatureFlags":
        return cls(
            hybrid_search=os.getenv("ENABLE_HYBRID_SEARCH", "true").lower() == "true",
            full_text_search=os.getenv("ENABLE_FULL_TEXT_SEARCH", "true").lower() == "true",
            context_expansion=os.getenv("ENABLE_CONTEXT_EXPANSION", "true").lower() == "true",
            query_rewriting=os.getenv("ENABLE_QUERY_REWRITING", "false").lower() == "true",
            response_streaming=os.getenv("ENABLE_RESPONSE_STREAMING", "false").lower() == "true"
        )


class Config:
    """Main configuration class - aggregates all config sections"""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.llm = LLMConfig.from_env()
        self.embedding = EmbeddingConfig.from_env()
        self.paths = PathConfig.from_env()
        self.processing = ProcessingConfig.from_env()
        self.cache = CacheConfig.from_env()
        self.features = FeatureFlags.from_env()
        
        # General settings
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration and return errors if any"""
        errors = []
        
        # Validate database config
        if not self.database.validate():
            errors.append("Database configuration incomplete (check SUPABASE_URL, SUPABASE_SERVICE_KEY, DB_PASSWORD)")
        
        # Validate LLM config
        if not self.llm.get_api_key():
            errors.append(f"LLM API key not set for provider: {self.llm.provider}")
        
        # Validate paths
        if not self.paths.json_folder.exists():
            errors.append(f"JSON folder not found: {self.paths.json_folder}")
        
        return (len(errors) == 0, errors)
    
    def print_config(self):
        """Print configuration summary (without secrets)"""
        print("=" * 70)
        print("RAG SYSTEM CONFIGURATION")
        print("=" * 70)
        print(f"Environment: {self.environment}")
        print(f"Debug Mode: {self.debug}")
        print(f"Log Level: {self.log_level}")
        print()
        print("DATABASE:")
        print(f"  Supabase URL: {self.database.supabase_url[:30]}...")
        print(f"  DB Host: {self.database.db_host}")
        print(f"  Pool Size: {self.database.pool_size}")
        print()
        print("LLM:")
        print(f"  Provider: {self.llm.provider}")
        print(f"  Model: {self.llm.get_model()}")
        print(f"  Max Context: {self.llm.max_context_length}")
        print()
        print("EMBEDDING:")
        print(f"  Model: {self.embedding.model_name}")
        print(f"  Dimension: {self.embedding.dimension}")
        print(f"  Batch Size: {self.embedding.batch_size}")
        print(f"  GPU: {self.embedding.use_gpu}")
        print()
        print("PATHS:")
        print(f"  JSON Folder: {self.paths.json_folder}")
        print(f"  Output: {self.paths.output_folder}")
        print(f"  Logs: {self.paths.logs_folder}")
        print()
        print("PROCESSING:")
        print(f"  DB Batch Size: {self.processing.db_batch_size}")
        print(f"  Top-K: {self.processing.default_top_k}")
        print(f"  Similarity Threshold: {self.processing.similarity_threshold}")
        print()
        print("FEATURES:")
        print(f"  Hybrid Search: {self.features.hybrid_search}")
        print(f"  Context Expansion: {self.features.context_expansion}")
        print(f"  Query Cache: {self.cache.enabled}")
        print("=" * 70)


# Global config instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    is_valid, errors = config.validate()
    
    if is_valid:
        config.print_config()
        print("\n✅ Configuration is valid!")
    else:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
