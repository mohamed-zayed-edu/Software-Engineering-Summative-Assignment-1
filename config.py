"""Configuration constants for the application."""
# Base URL for EES API
BASE_URL = "https://api.education.gov.uk/statistics/v1"

# Datasets
DATASETS = {
    "ks2-performance": "d32e9901-d5ef-b573-9993-06b9e9ed4e9d",
    "ks4-performance": "18e39901-7fe3-8372-8b2b-33f7ae1e1d12",
    "apprenticeships": "1d419801-a90e-f970-9335-a13623faccbe",
}

# Display titles
DATASET_TITLES = {
    "ks2-performance": "KS2 Performance",
    "ks4-performance": "KS4 Performance",
    "apprenticeships": "Apprenticeships",
}
