"""
Command-line interface for SERP Agent
"""
import os
from dotenv import load_dotenv
from .run_task import run_with_env_settings
from ..logging.logger import log


def main():
    """
    Main CLI entry point that reads from environment variables
    and maintains backward compatibility with the original script.
    """
    # Load .env file first
    load_dotenv()
    
    # Read environment variables (maintaining original names)
    query = os.getenv("SEARCH_QUERY", "novia virtual gratis")
    target = os.getenv("TARGET_DOMAIN", "noviachat.com")
    
    log(f"Starting search task: query='{query}', target='{target}'")
    
    # Execute the task using environment settings
    success = run_with_env_settings(query, target)
    
    if success:
        log("Task completed successfully")
    else:
        log("Task completed with no results")
    
    return success


if __name__ == "__main__":
    main()