select distinct region
from {{ ref('stg_shareholder_letter') }}