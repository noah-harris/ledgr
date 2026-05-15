import pandas as pd

def search(df:pd.DataFrame, fields:dict) -> pd.DataFrame:
    """
    query = {
        "Exact Column Name": {"value": value, "sort_ascending": True/False},
        }

    NOTE:
    The value provided in a field must match that of a dataframe
    """
    dtype_mapping = {
        'object': str,
        'int64': int,
        'float64': float,
        'datetime64[ns]': pd.Timestamp,
        'bool': bool,
        'str':str
    }
    sort_columns = []
    sort_ascending = []
    mask = pd.Series(True, index=df.index)
    any_filter = False
    
    for column, criteria in fields.items():
        sort = criteria.get("sort_ascending", None)
        if sort is not None:
            sort_columns.append(column)
            sort_ascending.append(sort)
        
        value = criteria.get("value", None)
        if value is not None:
            dtype = dtype_mapping.get(str(df[column].dtype))
            value = dtype(value)
            mask &= df[column] == value
            any_filter = True

    if not any_filter:
        return None
            
    if sort_columns:
        df = df.sort_values(by=sort_columns, ascending=sort_ascending)
    output:pd.DataFrame = df[mask]
    return output

def search_one(df:pd.DataFrame, fields:dict) -> tuple[dict, pd.DataFrame]:
    results = search(df, fields)

    num_results = len(results) if results is not None else 0

    match num_results:
        case 0:
            empty_dict = {col: None for col in df.columns}
            empty_result = pd.DataFrame([empty_dict])
            return None, empty_result
        case 1:
            return results.iloc[0].to_dict(), results
        case _:
            return None, results
