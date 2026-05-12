CREATE VIEW [v_Users]
    AS
SELECT 
    u.[UsersId], 
    u.[FirstName], 
    u.[LastName], 
    u.[FirstName] + ' ' + u.[LastName] AS [FullName],
    u.[Username], 
    u.[Email]
FROM [Users] AS u
