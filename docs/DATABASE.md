# Database Schema

## Tables

### users
Linked 1:1 with Supabase Auth (`id = auth.users.id`).

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | Same as Supabase Auth user id |
| dni | varchar(8) UNIQUE | Primary business identifier |
| full_name | varchar | May be null on import |
| emails | text[] | Can hold multiple emails |
| primary_email | varchar | Used for notifications |
| phone | varchar | Optional |
| role | enum | `participant` or `admin` |
| created_at / updated_at | timestamptz | Auto-managed |

### forms

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| title | varchar | Required |
| description | text | Optional |
| is_active | boolean | Controlled manually or by scheduler |
| opens_at | timestamptz | Null = manual open only |
| closes_at | timestamptz | Null = never auto-closes |
| created_by | uuid FK users | Admin who created it |

### questions

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| form_id | uuid FK | Cascades on form delete |
| order_index | integer | Controls display order |
| label | text | Question text |
| type | enum | `short_text`, `long_text`, `number`, `likert`, `single_choice`, `multiple_choice`, `date` |
| required | boolean | Default true |
| options | jsonb | Likert: `{min:1,max:5,min_label:'',max_label:''}` / Choice: `["opt1","opt2"]` |

### submissions
One row per (user, form) pair — enforced by UNIQUE constraint.

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| form_id / user_id | uuid FK | |
| submitted_at | timestamptz | Initial submission time |
| last_edited_at | timestamptz | Set on each PUT edit |
| edit_count | integer | Increments on each edit |
| admin_notified_of_edit | boolean | Reset to false on each edit |

### responses
One row per answer (submission + question pair).

| Column | Type | Notes |
|---|---|---|
| value | text | All types stored as text; cast on export |

### notifications_log
Audit trail for all sent emails.

| Column | Type | Values |
|---|---|---|
| type | enum | `reminder`, `edit_alert`, `deadline` |
| status | enum | `sent`, `failed` |
| channel | enum | `email` |

## Key Constraints
- `submissions(form_id, user_id)` is UNIQUE — prevents duplicate submissions
- All FK cascade on delete for questions and responses
- `users.dni` must be exactly 8 numeric digits (validated in API layer)
