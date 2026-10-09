select
    er.title_english,
    cast(er.release_date as date) as release_date,
    er.hours_viewed,
    er.views,
    er.runtime_hours,
    er.content_type
from {{ ref('stg_engagement_report') }} er