import time
from dataclasses import dataclass
from typing import Dict, List
import json
from datetime import datetime

@dataclass
class TestGenerationStats:
    total_files: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    errors: Dict[str, List[str]] = None
    
    def __init__(self):
        self.errors = {}
        self.start_time = time.time()
    
    def record_success(self):
        self.successful_generations += 1
        self.total_files += 1
    
    def record_failure(self, file_path: str, error: str):
        self.failed_generations += 1
        self.total_files += 1
        if file_path not in self.errors:
            self.errors[file_path] = []
        self.errors[file_path].append(error)
    
    def finish(self):
        self.end_time = time.time()
    
    def generate_report(self) -> str:
        duration = self.end_time - self.start_time
        success_rate = (self.successful_generations / self.total_files * 100) if self.total_files > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_files": self.total_files,
                "successful_generations": self.successful_generations,
                "failed_generations": self.failed_generations,
                "success_rate": f"{success_rate:.2f}%",
                "duration_seconds": f"{duration:.2f}",
            },
            "errors": self.errors
        }
        
        return json.dumps(report, indent=2)
