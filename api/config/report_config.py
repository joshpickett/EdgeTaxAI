from datetime import timedelta

REPORT_CONFIG = {
    # Test Generation Settings
    "TEST_SETTINGS": {
        "source_dirs": ["api/models", "api/middleware", "api/routes", "api/utils"],
        "test_base_dir": "tests",
        "default_test_type": "unit",
        "test_framework": "pytest",
        "batch_size": 5,
        "max_workers": 4,
        "rate_limit_delay": 1.0,
        "model_name": "gpt-4",
        "timeout": 30,
        "summary_file": "test_summary.txt",
    },
    "CACHE_SETTINGS": {
        "tax_summary": 3600,  # 1 hour
        "expense_report": 1800,  # 30 minutes
        "analytics_report": 7200,  # 2 hours
        "custom_report": 3600,  # 1 hour
    },
    "RATE_LIMITS": {
        "generate_report": 60,  # requests per minute
        "analytics": 30,  # requests per minute
        "export": 45,  # requests per minute
    },
    "REPORT_TYPES": {
        "tax_summary": {
            "allowed_formats": ["pdf", "excel", "json"],
            "cache_duration": timedelta(hours=1),
        },
        "expense_report": {
            "allowed_formats": ["pdf", "excel", "json"],
            "cache_duration": timedelta(minutes=30),
        },
        "analytics_report": {
            "allowed_formats": ["pdf", "json"],
            "cache_duration": timedelta(hours=2),
        },
    },
    "EXPORT_SETTINGS": {
        "pdf": {"page_size": "letter", "orientation": "portrait"},
        "excel": {"sheet_name": "Report Data", "date_format": "YYYY-MM-DD"},
    },
}
