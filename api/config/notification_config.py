NOTIFICATION_CONFIG = {
    "EMAIL": {
        "templates": {
            "document_expiration": {
                "subject": "Document Expiration Notice",
                "template_file": "document_expiration.html",
            },
            "validation_error": {
                "subject": "Document Validation Error",
                "template_file": "validation_error.html",
            },
            "status_change": {
                "subject": "Document Status Update",
                "template_file": "status_change.html",
            },
        },
        "from_email": "notifications@yourdomain.com",
        "reply_to": "support@yourdomain.com",
    },
    "IN_APP": {
        "retention_days": 30,
        "max_unread": 100,
        "priority_levels": ["high", "medium", "low"],
    },
    "NOTIFICATION_TYPES": {
        "EXPIRATION": {"warning_days": [30, 14, 7, 1], "priority": "high"},
        "VALIDATION": {"retry_count": 3, "priority": "medium"},
        "STATUS_CHANGE": {"priority": "low"},
    },
}
