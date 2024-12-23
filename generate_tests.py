import os
import logging
from openai import OpenAI
from api.config import Config
import time
import argparse
from typing import Optional, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from utils.test_statistics import TestGenerationStats
from utils.path_manager import PathManager
from utils.test_cache import TestCache
from utils.openai_handler import OpenAIHandler

stats = TestGenerationStats()
cache = TestCache()

# Initialize OpenAI handler
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Validate config and set API key
Config.validate()
openai_handler = OpenAIHandler(api_key=Config.OPENAI_API_KEY, max_retries=Config.MAX_RETRIES)

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
                
                response = openai_handler.generate_completion(
                    messages=[  # Updated message format
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
                    model=Config.MODEL_NAME,
                    timeout=Config.TIMEOUT
                )
                break
            except Exception as e:
                retries += 1
                if retries == Config.MAX_RETRIES:
                    raise
                time.sleep(2 ** retries)  # Exponential backoff

        # Extract the response content
        test_content = response.choices[0].message.content  # Updated response access

        # Cache the result
        cache.set(code_content, test_content)

        if not test_content.strip():
            raise ValueError("Received an empty response from the OpenAI API.")

        # Separate the test code and the summary
        if "### Summary of Tests" in test_content:
            test_code, test_summary = test_content.split("### Summary of Tests", 1)
        else:
            test_code, test_summary = test_content, "No summary provided."

        # Format the test summary as comments at the top of the file
        formatted_summary = "\n".join(f"# {line.strip()}" for line in test_summary.split("\n"))
        test_code = f"""# Test Summary:
{formatted_summary}

{test_code.strip()}"""

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

def process_file(source_file_path: str, test_file_path: str) -> None:
    """Process a single file to generate tests."""
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

def process_directories(path_manager: PathManager) -> None:
    """Process directories to create corresponding test files."""
    # Create all necessary test directories
    path_manager.create_test_directories()
    
    # Get all source files and their test paths
    files_to_process = path_manager.get_source_files()
     
    with ThreadPoolExecutor() as executor:
        executor.map(lambda x: process_file(x[0], x[1]), files_to_process)

def main():
    parser = argparse.ArgumentParser(description='Generate tests for Python files')
    parser.add_argument('--framework', type=str, choices=['pytest', 'unittest'], 
                        default=Config.TEST_FRAMEWORK, help='Test framework to use')
    args = parser.parse_args()

    Config.TEST_FRAMEWORK = args.framework

    # Initialize PathManager
    path_manager = PathManager(Config.TEST_MAPPING)
    
    # Validate paths
    invalid_paths = path_manager.validate_paths()
    if invalid_paths:
        log_progress(f"Error: The following source directories do not exist: {invalid_paths}")
        return

    log_progress("Starting test generation process...")
    process_directories(path_manager)
    
    stats.finish()
    with open('test_generation_stats.json', 'w') as f:
        f.write(stats.generate_report())
    
    log_progress("Test generation process completed.")

if __name__ == "__main__":
    main()
