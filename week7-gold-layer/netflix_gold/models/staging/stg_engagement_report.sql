select
    title_english,
    title_original,
    lower(trim(title_english)) as title_key,
    release_date,
    hours_viewed,
    views,
    runtime_hours,
    content_type
from {{ source('silver', 'engagement_report') }}