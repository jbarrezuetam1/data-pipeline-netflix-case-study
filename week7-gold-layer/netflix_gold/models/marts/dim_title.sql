select
    er.title_english,
    er.title_original,
    er.content_type,
    tm.genres,
    tm.vote_average,
    tm.budget,
    tm.status
from {{ ref('stg_engagement_report') }} er
left join {{ ref('stg_tmdb_movies') }} tm
    on er.title_key = tm.title_key