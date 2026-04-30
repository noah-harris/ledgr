CREATE FUNCTION [fn_StripNonAlphanumeric] (@Input VARCHAR(MAX))
RETURNS VARCHAR(MAX)
WITH SCHEMABINDING
AS
BEGIN
    IF @Input IS NULL RETURN NULL;

    DECLARE @Output VARCHAR(MAX) = '';
    DECLARE @Position INT = 1;
    DECLARE @Character CHAR(1);
    
    WHILE @Position <= LEN(@Input)
    BEGIN
        SET @Character = SUBSTRING(@Input, @Position, 1);

        IF @Character LIKE '[A-Za-z0-9]'
            SET @Output += @Character;

        SET @Position += 1;
    END

    RETURN @Output;
END;