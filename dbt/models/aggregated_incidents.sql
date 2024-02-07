select
    incident_date,
    battalion,
    supervisor_district as district,
    count(*) as total_incidents
from fire_incidents
group by 1, 2, 3