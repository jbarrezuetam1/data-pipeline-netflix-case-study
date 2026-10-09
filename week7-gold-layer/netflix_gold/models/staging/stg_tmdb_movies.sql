select
    title,
    lower(trim(title)) as title_key,
    release_date,
    runtime_minutes,
    budget,
    revenue,
    vote_average,
    genres,
    status
from {{ source('silver', 'tmdb_movies') }}