import os
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any
from api.config import Config
from itertools import islice
from utils.test_statistics import TestGenerationStats
from utils.test_cache import TestCache
from utils.openai_handler import OpenAIHandler

def setup_logging():
    """Configure logging for test generation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_test_directory(source_path: str, test_base_dir: str) -> str:
    """Create test directory structure mirroring source structure."""
    # Convert source path to test path
    relative_path = os.path.dirname(source_path)
    test_dir = os.path.join(test_base_dir, relative_path)
    
    # Create test directory if it doesn't exist
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

def get_test_file_path(source_file: str, test_dir: str) -> str:
    """Generate test file path from source file."""
    base_name = os.path.basename(source_file)
    if base_name.startswith('__'):
        return None
    test_file_name = f"test_{base_name}"
    return os.path.join(test_dir, test_file_name)

def process_file(source_path: str, test_path: str) -> None:
    """Process a single source file and generate its test file."""
    try:
        with open(source_path, 'r') as f:
            source_content = f.read()

        # Check cache first
        test_cache = TestCache()
        cached_content = test_cache.get(source_content)
        if cached_content:
            logging.info(f"Using cached tests for {source_path}")
            return cached_content

        # Generate new tests using OpenAI
        openai_handler = OpenAIHandler(Config.OPENAI_API_KEY)
        messages = [
            {"role": "system", "content": "You are a test generation assistant. Generate comprehensive tests for the given code."},
            {"role": "user", "content": f"Generate tests for:\n\n{source_content}"}
        ]
        estimated_tokens = sum(len(m['content'].split()) * 1.3 for m in messages)
        if not openai_handler.token_bucket.consume(int(estimated_tokens)):
            delay = openai_handler._calculate_wait_time(estimated_tokens)
            logging.info(f"Rate limit approaching. Waiting {delay:.2f} seconds...")
            time.sleep(delay)

        response = openai_handler.generate_completion(
            messages=messages,
            model=Config.MODEL_NAME,
            temperature=0.7,
            max_tokens=2000
        )
        test_content = response.choices[0].message.content

        # Cache the results
        test_cache.set(source_content, test_content)
        
        TestGenerationStats.get_instance().record_success()
        logging.info(f"Successfully generated tests for {source_path}")
    except Exception as e:
        TestGenerationStats.get_instance().record_failure(source_path, str(e))
        logging.error(f"Failed to generate tests for {source_path}: {str(e)}")

def batch_files(files, batch_size):
    """Process files in batches."""
    it = iter(files)
    while batch := list(islice(it, batch_size)):
        yield batch

def process_source_directories() -> None:
    """Process all configured source directories."""
    batch_size = Config.BATCH_SIZE
    max_workers = min(Config.MAX_WORKERS, batch_size)
    
    logging.info(f"Processing files in batches of {batch_size} with {max_workers} workers")

    source_dirs = Config.TEST_MAPPING['source_dirs']
    test_base_dir = Config.TEST_MAPPING['test_base_dir']
     
    files_to_process = []
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            logging.warning(f"Source directory not found: {source_dir}")
            continue
            
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    source_path = os.path.join(root, file)
                    test_dir = create_test_directory(source_path, test_base_dir)
                    test_path = get_test_file_path(source_path, test_dir)
                    if test_path:
                        files_to_process.append((source_path, test_path))

    # Process files in batches
    for batch in batch_files(files_to_process, batch_size):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda x: process_file(x[0], x[1]), batch)
        time.sleep(Config.RATE_LIMIT_DELAY)  # Add delay between batches

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description='Generate tests for Python files')
    parser.add_argument('--framework', type=str, choices=['pytest', 'unittest'], 
                       default=Config.TEST_FRAMEWORK, help='Test framework to use')
    args = parser.parse_args()

    Config.TEST_FRAMEWORK = args.framework
    process_source_directories()
    TestGenerationStats.print_summary()

if __name__ == "__main__":
    main()
