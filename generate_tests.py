import os
import openai
import logging
from openai import OpenAI, APIError, RateLimitError, APITimeoutError
from openai.types.error import APIError as OpenAIError
import time
import argparse
from typing import Optional, Dict, Any
from dataclasses import dataclass
from api.config import Config
from concurrent.futures import ThreadPoolExecutor
from utils.test_statistics import TestGenerationStats
from utils.test_cache import TestCache

stats = TestGenerationStats()
cache = TestCache()

# Initialize OpenAI client
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Validate config and set API key
Config.validate()
client = OpenAI(api_key=Config.OPENAI_API_KEY)

@dataclass
class TestGenerationResult:
    """Data class to hold test generation results"""
    content: str
    summary: str
    success: bool
    error: Optional[str] = None

def log_progress(message):
    """Log progress to both the console and the log file."""
    print(message)
    logging.info(message)

def generate_tests(source_file_path: str, test_file_path: str, code_content: str) -> TestGenerationResult:
    """Generates unit tests using OpenAI and writes them to the test file.
    
    Args:
        source_file_path: Path to the source file being tested
        test_file_path: Path where the generated test will be written
        code_content: Content of the source file to generate tests for
        
    Returns:
        TestGenerationResult object containing the generated content and metadata
    """
    retries = 0
    try:
        while retries < Config.MAX_RETRIES:
            # Check cache first
            cached_content = cache.get(code_content)
            if cached_content:
                return TestGenerationResult(
                    content=cached_content,
                    summary="",
                    success=True
                )

            try:
                log_progress(f"Generating tests for: {source_file_path}")
                
                response = client.chat.completions.create(
                    model=Config.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a professional software engineer specialized in writing tests."},
                        {
                            "role": "user", 
                            "content": f"""Write {Config.TEST_FRAMEWORK} tests for the following code:
                                Include:
                                - Edge cases and boundary conditions
                                - Error handling scenarios
                                - Performance considerations
                                - Security testing where applicable
                                - A comprehensive test summary
                                Code to test:\n\n{code_content}"""
                        }
                    ],
                    timeout=Config.TIMEOUT
                )
                break
            except (RateLimitError, APITimeoutError, APIError) as e:
                retries += 1
                if retries == Config.MAX_RETRIES:
                    raise
                time.sleep(2 ** retries)  # Exponential backoff

        # Extract the response content
        test_content = response.choices[0].message["content"]

        # Cache the result
        cache.set(code_content, test_content)

        if not test_content.strip():
            raise ValueError("Received an empty response from the OpenAI API.")

        # Separate the test code and the summary
        if "### Summary of Tests" in test_content:
            test_code, test_summary = test_content.split("### Summary of Tests", 1)
        else:
            test_code, test_summary = test_content, "No summary provided."

        # Add metadata header to the test file
        feature_description = f"""
        \"\"\"
        Test Suite for {os.path.basename(source_file_path)}

        Feature Tested: 
        {test_summary.strip()}

        \"\"\"
        """
        test_code = feature_description + "\n" + test_code.strip()

        # Write the generated test to the test file
        with open(test_file_path, "w") as test_file:
            test_file.write(test_code)
        log_progress(f"Test file created: {test_file_path}")

        # Append the summary to the summary file
        summary_file_path = os.path.join(Config.TESTS_ROOT, Config.SUMMARY_FILE)
        with open(summary_file_path, "a") as summary_file:
            summary_file.write(f"Test Summary for {source_file_path}:\n")
            summary_file.write(test_summary.strip() + "\n\n")

        stats.record_success()
        return TestGenerationResult(
            content=test_content,
            summary=test_summary,
            success=True
        )

    except Exception as e:
        error_message = f"Error generating test for {source_file_path}: {e}"
        log_progress(error_message)
        logging.error(error_message)
        stats.record_failure(source_file_path, str(e))
        return TestGenerationResult(
            content="",
            summary="",
            success=False,
            error=str(e)
        )

def process_file(root: str, file_name: str, target_subdir: str) -> None:
    """Process a single file to generate tests."""
    source_file_path = os.path.join(root, file_name)
    test_file_name = f"test_{file_name}"
    test_file_path = os.path.join(target_subdir, test_file_name)

    try:
        # Read the source file content
        with open(source_file_path, "r") as source_file:
            code_content = source_file.read()

        if not code_content.strip():
            log_progress(f"Skipping empty file: {source_file_path}")
            return

        # Generate tests for the source file
        generate_tests(source_file_path, test_file_path, code_content)
    except Exception as e:
        log_progress(f"Error processing file {source_file_path}: {e}")
        logging.error(f"Error processing file {source_file_path}: {e}")

def process_directory(source_dir: str, target_dir: str) -> None:
    """Recursively process a directory to create corresponding test files."""
    files_to_process = []
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path of the current directory
        relative_path = os.path.relpath(root, source_dir)
        # Create the corresponding directory in the tests folder
        target_subdir = os.path.join(target_dir, relative_path)
        os.makedirs(target_subdir, exist_ok=True)
        
        files_to_process.extend([
            (root, file_name, target_subdir)
            for file_name in files
            if file_name.endswith(".py")
        ])
    
    # Process files concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(lambda x: process_file(*x), files_to_process)

def main():
    parser = argparse.ArgumentParser(description='Generate tests for Python files')
    parser.add_argument('--source', type=str, help='Source directory', default=Config.SOURCE_ROOT)
    parser.add_argument('--target', type=str, help='Target directory', default=Config.TESTS_ROOT)
    parser.add_argument('--framework', type=str, choices=['pytest', 'unittest'], 
                        default=Config.TEST_FRAMEWORK, help='Test framework to use')
    args = parser.parse_args()

    # Update config based on arguments
    Config.SOURCE_ROOT = args.source
    Config.TESTS_ROOT = args.target
    Config.TEST_FRAMEWORK = args.framework

    # Clear the summary file at the start
    summary_file_path = os.path.join(Config.TESTS_ROOT, Config.SUMMARY_FILE)
    if os.path.exists(summary_file_path):
        os.remove(summary_file_path)

    log_progress("Starting test generation process...")
    
    # Start processing
    process_directory(Config.SOURCE_ROOT, Config.TESTS_ROOT)
    
    # Generate final statistics
    stats.finish()
    with open('test_generation_stats.json', 'w') as f:
        f.write(stats.generate_report())
    
    log_progress("Test generation process completed.")

if __name__ == "__main__":
    main()
