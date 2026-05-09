#!/bin/bash
# task_approval_check - Check if a workday task requires approval and get its status
INPUT=$(cat)
echo "{\"result\": \"ok\", \"skill\": \"task_approval_check\", \"input\": $INPUT}"
