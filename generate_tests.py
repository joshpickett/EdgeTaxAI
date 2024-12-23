import os
import openai
import logging

# Set up logging
logging.basicConfig(
    filename="test_generation_debug.log", 
    level=logging.DEBUG, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set your OpenAI API key
openai.api_key = "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"

# Define the root folder to iterate through and the destination tests folder
source_root = "api/Routes"  # Specify the folder to iterate through
tests_root = "tests/API/Routes"       # Matching folder structure in tests

# Create the root tests folder if it doesn't exist
os.makedirs(tests_root, exist_ok=True)

# File to store the summary
summary_file_path = os.path.join(tests_root, "test_summary.log")


def log_progress(message):
    """Log progress to both the console and the log file."""
    print(message)
    logging.info(message)


def generate_tests(source_file_path, test_file_path, code_content):
    """Generates unit tests using OpenAI and writes them to the test file."""
    try:
        log_progress(f"Generating tests for: {source_file_path}")
        
        # Generate tests using OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional software engineer."},
                {"role": "user", "content": f"Write unit tests for the following code. Include edge cases, a test summary, and a description of the feature being tested:\n\n{code_content}"}
            ]
        )

        # Extract the response content
        test_content = response.choices[0].message["content"]

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
        with open(summary_file_path, "a") as summary_file:
            summary_file.write(f"Test Summary for {source_file_path}:\n")
            summary_file.write(test_summary.strip() + "\n\n")

    except Exception as e:
        error_message = f"Error generating test for {source_file_path}: {e}"
        log_progress(error_message)
        logging.error(error_message)


def process_directory(source_dir, target_dir):
    """Recursively process a directory to create corresponding test files."""
    for root, dirs, files in os.walk(source_dir):
        # Get the relative path of the current directory
        relative_path = os.path.relpath(root, source_dir)
        # Create the corresponding directory in the tests folder
        target_subdir = os.path.join(target_dir, relative_path)
        os.makedirs(target_subdir, exist_ok=True)

        # Process each file in the directory
        for file_name in files:
            if file_name.endswith(".py"):  # Only process Python files
                source_file_path = os.path.join(root, file_name)
                test_file_name = f"test_{file_name}"
                test_file_path = os.path.join(target_subdir, test_file_name)

                try:
                    # Read the source file content
                    with open(source_file_path, "r") as source_file:
                        code_content = source_file.read()

                    if not code_content.strip():
                        log_progress(f"Skipping empty file: {source_file_path}")
                        continue

                    # Generate tests for the source file
                    generate_tests(source_file_path, test_file_path, code_content)
                except Exception as e:
                    log_progress(f"Error processing file {source_file_path}: {e}")
                    logging.error(f"Error processing file {source_file_path}: {e}")


# Clear the summary file at the start
if os.path.exists(summary_file_path):
    os.remove(summary_file_path)

log_progress("Starting test generation process...")

# Start processing the designated folder
process_directory(source_root, tests_root)

log_progress("Test generation process completed.")

