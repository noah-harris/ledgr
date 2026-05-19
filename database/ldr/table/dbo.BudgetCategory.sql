CREATE TABLE [BudgetCategory] (
    [BudgetCategoryId] UNIQUEIDENTIFIER NOT NULL,
    [BudgetId] UNIQUEIDENTIFIER NOT NULL,
    [Segment] NVARCHAR(50) NULL,
    [Category] NVARCHAR(100) NULL,
    [SubCategory] NVARCHAR(100) NULL,
    [Amount] DECIMAL(18, 2) NOT NULL,
    PRIMARY KEY NONCLUSTERED ([BudgetCategoryId]),
    CONSTRAINT [FK_BudgetCategory_Budget] FOREIGN KEY ([BudgetId]) REFERENCES [Budget]([BudgetId])
);