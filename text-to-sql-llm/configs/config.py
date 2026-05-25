class Config:
    # Model settings
    OPENAI_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Retrieval settings
    TOP_K = 3
    
    # Self-correction settings
    MAX_CORRECTIONS = 2
    
    # Data paths
    SPIDER_DATA_DIR = "data/spider"
    PROCESSED_DATA_DIR = "data/processed"
    
    # Database settings
    DB_DIR = "data/databases"
