#!/bin/bash
#1.print a message to the terminal
echo "Running the stock analysis pipeline..."
#2. Run the Python script
python3 pipeline.py
#3. Check if the Python script ran successfully
if [ $? -eq 0 ]; then
    echo "Pipeline executed successfully."
else
    echo "Pipeline execution failed."
fi