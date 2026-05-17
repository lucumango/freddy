# User Stories

## Participant

- As a participant, I can log in with my DNI and password
- As a participant, I can see all active forms available to me
- As a participant, I can submit answers to a form (one submission per form)
- As a participant, I can edit my submitted answers while the form is still active
- As a participant, I can view my own submitted answers
- As a participant, I can link additional email addresses to my account
- As a participant, I can link a phone number to my account
- As a participant, I can change my password
- As a participant, I receive a reminder email when I have a pending form
- As a participant, I receive a warning email 24h before a form closes

## Admin

- As an admin, I can register new participants by DNI
- As an admin, I can bulk-import participants from a CSV file
- As an admin, I can preview an import (dry run) before committing it
- As an admin, I can create forms with multiple question types
- As an admin, I can add, edit, reorder, and remove questions from a form
- As an admin, I can manually open or close a form
- As an admin, I can schedule forms to auto-open and auto-close at specific times
- As an admin, I can see who has submitted and who is pending for any form
- As an admin, I can send reminder emails to pending participants (with 24h cooldown)
- As an admin, I receive an email alert when a participant edits their submission
- As an admin, I can export all responses as CSV or Excel
- As an admin, I can export a completion summary (users x forms pivot)
- As an admin, I can export a report of incomplete user profiles
- As an admin, I can see which users have data quality issues (missing DNI, name, email)

## System (automated)

- Every hour, forms with a past `opens_at` are automatically activated
- Every hour, forms with a past `closes_at` are automatically deactivated
- Daily at 9am Lima time, deadline warning emails are sent to users with forms closing within 24h
