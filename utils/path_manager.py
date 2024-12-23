import os
from typing import Dict, List, Tuple
import logging
from api.config import Config

class PathManager:
    """Manages source and test path mappings and directory creation."""
    
    def __init__(self, test_mapping: Dict[str, str]):
        self.test_mapping = test_mapping
        
    def create_test_directories(self) -> None:
        """Create all necessary test directories if they don't exist."""
        for test_dir in self.test_mapping.values():
            os.makedirs(test_dir, exist_ok=True)
            logging.info(f"Ensured test directory exists: {test_dir}")
            
    def get_test_path(self, source_path: str) -> str:
        """Convert a source file path to its corresponding test file path."""
        for source_directory, test_directory in self.test_mapping.items():
            if source_path.startswith(source_directory):
                relative_path = os.path.relpath(source_path, source_directory)
                test_file_name = f"test_{os.path.basename(relative_path)}"
                return os.path.join(test_directory, test_file_name)
        raise ValueError(f"No test mapping found for source path: {source_path}")
    
    def validate_paths(self) -> List[str]:
        """Validate all source directories exist."""
        invalid_paths = []
        for source_directory in self.test_mapping.keys():
            if not os.path.exists(source_directory):
                invalid_paths.append(source_directory)
        return invalid_paths
    
    def get_source_files(self) -> List[Tuple[str, str]]:
        """Get all source files and their corresponding test paths."""
        source_files = []
        for source_directory in self.test_mapping.keys():
            for root, _, files in os.walk(source_directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        source_path = os.path.join(root, file)
                        test_path = self.get_test_path(source_path)
                        source_files.append((source_path, test_path))
        return source_files
