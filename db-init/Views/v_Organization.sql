CREATE VIEW [v_Organization] 
    AS
SELECT 
    o.[OrganizationId],
    o.[OrganizationTypeId],
    o.[OrganizationName],
    ot.[OrganizationTypeName],
    ot.[IsAccountProvider],
    ot.[Segment],
    o.[Description]
FROM [Organization] AS o
JOIN [OrganizationType] AS ot ON o.[OrganizationTypeId] = ot.[OrganizationTypeId]