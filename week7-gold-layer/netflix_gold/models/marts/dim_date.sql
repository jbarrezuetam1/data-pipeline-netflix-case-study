select distinct
    try_cast(release_date as date) as date_day,
    extract(year from try_cast(release_date as date)) as year,
    extract(quarter from try_cast(release_date as date)) as quarter,
    extract(month from try_cast(release_date as date)) as month
from {{ ref('stg_engagement_report') }}
where try_cast(release_date as date) is not null

union

select distinct
    try_cast(release_date as date) as date_day,
    extract(year from try_cast(release_date as date)) as year,
    extract(quarter from try_cast(release_date as date)) as quarter,
    extract(month from try_cast(release_date as date)) as month
from {{ ref('stg_tmdb_movies') }}
where try_cast(release_date as date) is not null