select distinct
    cast(release_date as date) as date_day,
    extract(year from cast(release_date as date)) as year,
    extract(quarter from cast(release_date as date)) as quarter,
    extract(month from cast(release_date as date)) as month
from {{ ref('stg_engagement_report') }}
where release_date is not null

union

select distinct
    cast(release_date as date) as date_day,
    extract(year from cast(release_date as date)) as year,
    extract(quarter from cast(release_date as date)) as quarter,
    extract(month from cast(release_date as date)) as month
from {{ ref('stg_tmdb_movies') }}
where release_date is not null