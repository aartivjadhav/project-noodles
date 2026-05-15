 # The logger.py file is used to create a unified logger for the entire ETL pipeline, helping to monitor script execution progress, debug errors, and verify whether tasks have been completed.
import logging
# 👉 Standard Python logging library
# 👉 Used to print logs to the terminal (INFO, ERROR, ...)

def setup_logger(name: str):
    # 👉 Function to create a logger with a unique name for each module (e.g., powerbi_prep, aggregations)

    logger = logging.getLogger(name)
    # 👉 Get (or create) a logger based on the name provided
    
    logger.setLevel(logging.INFO)
    # 👉 Only log from the INFO level and above
    # 👉 DEBUGs will not be printed

    if not logger.handlers:
        # 👉 Avoid adding handlers multiple times when importing multiple files
        
        handler = logging.StreamHandler()
        # 👉 The log will be printed to the terminal/console

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
        )
        # 👉 Format log:
        # 👉 [time] LEVEL - logger name - log content

        handler.setFormatter(formatter)
        # 👉 Apply formatting to the handle

        logger.addHandler(handler)
        # 👉 Attach the handle to the logger

    return logger
    # 👉 Return the logger so other files can use it.