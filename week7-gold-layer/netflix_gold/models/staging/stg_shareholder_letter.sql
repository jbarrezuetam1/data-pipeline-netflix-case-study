select
    region,
    quarter_label,
    quarter_end_date,
    revenue_millions,
    yoy_growth_pct,
    fx_neutral_yoy_growth_pct
from {{ source('silver', 'shareholder_letter_regional_breakdown') }}