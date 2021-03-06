import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta 

def gen_plotly_dict(selection_list, df, dropdown_tag, precision=None):
    """
    Function to create a list of dictionaries for use in a dynamic plotly plot.

    Creates dictionary objects from slices of data from a source dataframe.
    Text data is optionally rounded for display.
    These are appended to a list that is the length of the number of slices created.

    Args:
        selection_list (list): Contains values to slice the source dataframe on.
        df (pandas.core.frame.DataFrame): Source to create dict objects from
        dropdown_tag (str): The column that contains the timestamp values.
        precision (int | None): If set to an integer defines the number of decimals for floating point rounding.

    Returns:
        dropdown_ar (list): Contains a number of dictionaries that can be displayed dynamically by a plotly plot.
    """
    dropdown_ar = []
    for selection in selection_list:
        # Select a data slice
        selected_value = df[df[dropdown_tag] == selection].drop(dropdown_tag, axis=1).values
        # Round values if precision is determined
        if precision is not None:
            text_values = np.around(selected_value.astype(float), precision)
        else:
            text_values = selected_value
        # Create a dict object for each slice
        temp_dict = dict(args=[{"y": selected_value, "text": text_values}], label=selection, method="restyle")
        # Add to the final array
        dropdown_ar.append(temp_dict)
    return dropdown_ar


def preprocess_data(initial_data, x_labels, dropdown_tag, precision=None):
    """
    Function to prepare a Pandas Series to be displayed in a waterfall plot.

    Splits out processes relevant data from a Pandas series to create the input for a waterfall plot.
    The datetime entry is dropped from the Series by name using enumerate inside a list comprehension.

    Args:
        initial_data (pandas.core.series.Series): Contains the initial data to display.
        x_labels (list): Defines the names for the columns to plot.
        dropdown_tag (str): The column that contains the timestamp values.
        precision (int | None): If set to an integer defines the number of decimals for floating point rounding.

    Returns:
        list(x_labels) (list): Contains the column names for a waterfall plot
        y_values (list): Values to plot.
        disp_values (numpy.ndarray): Values to display as text in the waterfall plot
    """
    # Remove the dropdown column values and label so that it is not displayed in initial plot
    y_values = list(initial_data)
    # Find the index of the dropdown tag
    indices = [i for i, item in enumerate(x_labels) if dropdown_tag in item][0]
    # Remove those indexes in the initial data
    del x_labels[indices]
    del y_values[indices]
    # Round values if precision is determined
    if precision is not None:
        disp_values = np.around(np.asarray(y_values).astype(float), precision)
    else:
        disp_values = np.asarray(y_values)

    return list(x_labels), y_values, disp_values


def plot_waterfall(measures, dropdown_tag, x_labels, y_values, disp_values, dicts_ar, title=None):
    """
    Function to display waterfall plots with a dropdown selector in plotly.

    Different data slices can be selected by timestamp from a dropdown selection menu.
    These slices of data are contained within dictionary objects passes as a list to fig.update_layout.
    Code assumes that dropdown information shouldn't be plotted.

    Args:
        measures (list): Defines the type of column to plot in the waterfall - 'absolute' or 'relative'.
        dropdown_tag (str): The column that contains the timestamp values.
        x_labels (list): Defines the names for the columns to plot.
        y_labels (list): Initial data to plot.
        disp_values (numpy.ndarray) Initial data to display.
        dicts_ar (list): List of dicts containing data to be passed to fig.update_layout.
        title (str): Plot title to be displayed.

    Returns:
        None
    """
    # Define the initial plot
    fig = go.Figure(go.Waterfall(
        orientation = "v",
        measure = measures,
        x = x_labels,
        textposition = "outside",
        y = y_values,
        text = disp_values,
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))

    # Add dynamic plot that is built from the dicts inside dicts_ar
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=dicts_ar,
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                xanchor="auto",
                x=0.25,
                yanchor="top",
                y=1.2
            ),
        ]
    )

    fig.update_layout(
            title = title,
            showlegend = False
    )

    fig.show()


def create_dropdown_waterfall(df, dropdown_tag, measures, initial_data, precision=None, title=None):
    """
    Function that processes a pandas dataframe so that a waterfall plot can be created.

    Helps to abstract several data preparation stages for creating a waterfall plot with a dropdown selector.

    Args:
        df (pandas.core.frame.DataFrame): Holds the data to plot.
        dropdown_tag (str): The column that contains the timestamp values.
        measures (list): Defines the type of column to plot in the waterfall - 'absolute' or 'relative'.
        initial_data (pandas.core.series.Series): Contains the initial data to display.
        precision (int | None): If set to an integer defines the number of decimals for floating point rounding.
        title (str): Plot title to be displayed.

    Returns:
        None
    """
    # Create the list to dynamically plot on
    dropdown_list = list(df[dropdown_tag].values)
    # Create the dicts for dropdown selections
    dicts_ar = gen_plotly_dict(dropdown_list, df, dropdown_tag, precision=precision)
    # Column labels set as waterfall labels
    columns_ar = list(df.columns)
    # Preprocess data to pass to plotting function
    x_labels, y_values, disp_values = preprocess_data(initial_data, columns_ar, dropdown_tag, precision=precision)
    plot_waterfall(measures, dropdown_tag, x_labels, y_values, disp_values, dicts_ar, title=title)


def extract_daterange(df, start_date, end_date):
    """
    Function that extracts rows of a dataframe between two dates.

    Selects rows that matcha a > and <= comparison to start and end dates.

    Args:
        df (pandas.core.frame.DataFrame): Holds the data to plot.
        start_date (str): Date to get rows after.
        start_date (str): Date to stop getting rows after (inclusive).

    Returns:
        selected_df (pandas.core.frame.DataFrame): Matching rows.
    """
    mask = (df.index > start_date) & (df.index <= end_date)
    selected_df = df.loc[mask]
    return selected_df


def create_date_ranges(target_date, date_range):
    """
    Function that creates a range of dates around a given date.

    For a given day the function generates a date x number of days before and then x number of days after and 2x days after.
    This is returned as a tuple holding 4 dates.

    Args:
        target_date (str): Date to generate boundaries around.
        date_range (int): x number of days to generate boundaries with.

    Returns:
        (tuple): tuple containing:

            start_date_1 (str): target_date - x days
            end_date_1 (str): target_date
            start_date_2 (str): target_date + x days
            end_date_2 (str): target_date + 2x days
    """
    f_date = datetime.strptime(target_date, '%Y-%m-%d')
    start_date_1 = f_date - timedelta(days=date_range)
    end_date_1 = f_date
    
    start_date_2 = f_date + timedelta(days=date_range)
    end_date_2 = f_date + timedelta(days=date_range*2)
    return start_date_1, end_date_1, start_date_2, end_date_2


def plot_change(x1, x2, tag, change, date, group_labels, bn_size):
    """
    Function that plots two datasets on either side of a date against each other.

    Uses a Plotly distplot to compare two pandas series on either side of a date on the same axis.

    Args:
        x1 (pandas.core.series.Series): Dataset 1.
        x2 (pandas.core.series.Series): Dataset 2.
        tag (str): Name of the datapoint to use in the plot title.
        change (str): Event that the two datasets are split on.
        date (str): Date of the event that the two datasets are split on.
        group_labels (list): Legend entries for the plot.
        bn_size (float): Bin size for the plot
    
    Returns:
        None
    """
    print(f'Set 1 points: {x1.shape}\nSet 2 points points: {x2.shape} ')
    hist_data = [x1, x2]

    fig = ff.create_distplot(hist_data, group_labels, bin_size = bn_size)
    fig.update_layout(title_text=f'{tag} before and after {change} on {date}')
    fig.show()


def get_dates(date_ar, d_format):
    """
    Function that converts a list of dates into a month abbreviation and year string.

    Uses the known date format to apply strptime and parse the human friendly month and year from a given list of dates.

    Args:
        date_ar (list): Dates to convert.
        d_format (str): Date format of the input dates.
    
    Returns:
        human_dates (list): Contains the converted dates as strings.
    """
    human_dates = []
    for date in date_ar:
        str_date = datetime.strptime(date, d_format).strftime("%b") + ' ' + str(datetime.strptime(date, d_format).year)
        human_dates.append(str_date)
    return human_dates


def plot_compare_timeframes(df, date1, date2, tag, filter_dict, tag_dict, date_dict, bin_dict, date_labels, date_range):
    """
    Function that plots two datasets from different dates against each other.

    Uses a Plotly distplot to compare two pandas series each representing a timeperiod on the same axis.

    Args:
        df (pandas.core.frame.DataFrame): Holds the source data to plot.
        date1 (str): The first date to extract data around.
        date2 (str): The second date to extract data around.
        tag (str): The name of the column to plot data from.
        filter_dict (dict): The filter conditions for various tags.
        tag_dict (dict): The nice names for each tag string.
        date_dict (dict): The events on each date.
        bin_dict (dict): The bin sizes for each tag
        date_labels (list): The abbreviated dates to use in legend.
        date_range (int): The number of dayes around each date to extract data for.
    
    Returns:
        None
    """
    date_ar = create_date_ranges(date1, date_range)
    date_df_1 = extract_daterange(df, date_ar[2], date_ar[3])

    date_ar = create_date_ranges(date2, date_range)
    date_df_2 = extract_daterange(df, date_ar[2], date_ar[3])

    # filters
    b_tag_df = date_df_1[tag]
    b_tag_df = b_tag_df[b_tag_df >= filter_dict[tag]]

    a_tag_df = date_df_2[tag]
    a_tag_df = a_tag_df[a_tag_df >= filter_dict[tag]]

    plot_change(b_tag_df.dropna(), a_tag_df.dropna(), tag_dict[tag], date_dict['comp'], date2, date_labels, bin_dict[tag])
    