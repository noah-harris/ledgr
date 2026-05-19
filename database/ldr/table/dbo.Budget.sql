CREATE TABLE [Budget] (
    [UsersId] UNIQUEIDENTIFIER NOT NULL,
    [BudgetId] UNIQUEIDENTIFIER NOT NULL,
    [BudgetName] NVARCHAR(100) NOT NULL,
    [StartDate] DATETIME2(0) NOT NULL,
    [EndDate] DATETIME2(0) NOT NULL,
    PRIMARY KEY NONCLUSTERED ([BudgetId]),
    CONSTRAINT [FK_Budget_User] FOREIGN KEY ([UsersId]) REFERENCES [Users]([UsersId]),
    CONSTRAINT [UQ_Budget_User_BudgetName] UNIQUE ([UsersId], [BudgetName]),
    CHECK (DATEDIFF(DAY, [StartDate], [EndDate]) >= 0) -- Ensure EndDate is not before StartDate
);