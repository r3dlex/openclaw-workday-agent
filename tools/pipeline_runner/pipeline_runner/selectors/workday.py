"""Workday DOM selectors as format-string constants.

Selectors that require interpolation (e.g. provider name) use Python
str.format() placeholders like ``{name}``.  Plain selectors are literal
strings ready for use with Playwright locators.
"""

# --- SSO / Authentication ---
SSO_PROVIDER_BUTTON = 'button:has-text("{name}"), div[role="button"]:has-text("{name}")'

# --- Task Actions ---
APPROVE_BUTTON = 'button:has-text("Approve"), div[role="button"]:has-text("Approve")'
DENY_BUTTON = 'button:has-text("Deny"), div[role="button"]:has-text("Deny")'
SEND_BACK_BUTTON = 'button:has-text("Send Back"), div[role="button"]:has-text("Send Back")'
SUBMIT_BUTTON = 'button:has-text("Submit"), div[role="button"]:has-text("Submit")'

# --- Task List ---
TASK_LIST_ITEMS = '[data-automation-id="taskListItem"], [role="listitem"][class*="task"]'
TASK_TITLE = '[data-automation-id="taskTitle"], [class*="task-title"]'
TASK_TYPE = '[data-automation-id="taskType"], [class*="task-type"]'
TASK_DATE = '[data-automation-id="taskDate"], [class*="task-date"]'
TASK_DESCRIPTION = '[data-automation-id="taskDescription"], [class*="task-description"]'

# --- Time Tracking ---
TIME_ENTRY_ROW = '[data-automation-id="timeEntryRow"], tr[class*="time-entry"]'
TIME_ENTRY_HOURS = '[data-automation-id="timeEntryHours"], input[class*="hours"]'
TIME_ENTRY_DATE = '[data-automation-id="timeEntryDate"], [class*="entry-date"]'

# --- Confirmation / Dialogs ---
CONFIRMATION_DIALOG = '[data-automation-id="confirmationDialog"], [role="dialog"]'
DONE_BUTTON = 'button:has-text("Done"), div[role="button"]:has-text("Done")'
