import numpy as np
import plotly.graph_objects as go

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
