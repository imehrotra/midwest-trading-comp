# CS121 Linear regression
#
# James Kon 

import numpy as np
from asserts import assert_Xy, assert_Xbeta

# because Guido van Rossum hates functional programming
# http://www.artima.com/weblogs/viewpost.jsp?thread=98196
from functools import reduce


#############################
#                           #
#  Our code: DO NOT MODIFY  #
#                           #
#############################


def prepend_ones_column(A):
    '''
    Add a ones column to the left side of an array

    Inputs: 
        A: a numpy array

    Output: a numpy array
    '''
    ones_col = np.ones((A.shape[0], 1))
    return np.hstack([ones_col, A])


def linear_regression(X, y):
    '''
    Compute linear regression. Finds model, beta, that minimizes
    X*beta - Y in a least squared sense.

    Accepts inputs with type array
    Returns beta, which is used only by apply_beta

    Examples
    --------
    >>> X = np.array([[5, 2], [3, 2], [6, 2.1], [7, 3]]) # predictors
    >>> y = np.array([5, 2, 6, 6]) # dependent
    >>> beta = linear_regression(X, y)  # compute the coefficients
    >>> beta
    array([ 1.20104895,  1.41083916, -1.6958042 ])
    >>> apply_beta(beta, X) # apply the function defined by beta
    array([ 4.86363636,  2.04195804,  6.1048951 ,  5.98951049])
    '''
    assert_Xy(X, y, fname='linear_regression')

    X_with_ones = prepend_ones_column(X)

    # Do actual computation
    beta = np.linalg.lstsq(X_with_ones, y)[0]

    return beta


def apply_beta(beta, X):
    '''
    Apply beta, the function generated by linear_regression, to the
    specified values

    Inputs:
        model: beta as returned by linear_regression
        Xs: 2D array of floats

    Returns:
        result of applying beta to the data, as an array.

        Given:
            beta = array([B0, B1, B2,...BK])
            Xs = array([[x11, x12, ..., x0K],
                        [x21, x22, ..., x1K],
                        ...
                        [xN1, xN2, ..., xNK]])

            result will be:
            array([B0+B1*x11+B2*x12+...+BK*x1K,
                   B0+B1*x21+B2*x22+...+BK*x2K,
                   ...
                   B0+B1*xN1+B2*xN2+...+BK*xNK])
    '''
    assert_Xbeta(X, beta, fname='apply_beta')

    # Add a column of ones
    X_incl_ones = prepend_ones_column(X)

    # Calculate X*beta
    yhat = np.dot(X_incl_ones, beta)
    return yhat


def read_file(filename):
    '''
    Read data from the specified file.  Split the lines and convert
    float strings into floats.  Assumes the first row contains labels
    for the columns.

    Inputs:
      filename: name of the file to be read

    Returns:
      (list of strings, 2D array)
    '''
    with open(filename) as f:
        labels = f.readline().strip().split(',')
        data = np.loadtxt(f, delimiter=',', dtype=np.float64)
        return labels, data


def print_models(trained_models, col_names):
    '''
    This function prints the models after the modesl have been generated. 
    Inputs:
        trained_models: a list of generated models dictioanry from the tasks
        col_names: the names of the columns
    '''
    for trained_model in trained_models: 
        variables = trained_model["indicies"]
        r_squared = trained_model["r_squared"]
        variable_names = []

        for variable in variables:
            variable_names.append(col_names[variable])

        clean_variable_names = ",".join(variable_names)
        print("{} R2: {:.2F}".format(clean_variable_names, r_squared))
    print()

def get_model(variables, dependent, data):
    '''
    This function returns a dictionary that contains information about the model based on 
    certain independent variables.
    Inputs:
        Variables: a list of the independent variables
        dependent: the index of the dependent variable
        data: the training data
    Output:
        model_dictionary: returns a copy of the model in a dictionary, contains information 
        about the dependent variables, the regression, the independent and dependent array
    '''
    independent_array = data[:, variables]
    dependent_array = data[:, dependent]
    regression = linear_regression(independent_array, dependent_array)
    
    model_dictionary = {"indicies": variables, "regression": regression, "independent_array": independent_array}
    model_dictionary["dependent_array"] = dependent_array

    return model_dictionary

def get_variance(model):
    '''
    This function computes the r_sqaured of a model. 
    Inputs:
        model: a singular model, passed as a dictioanry
    Outputs:
        r_squared: the r_squared value for the passed model
    '''
    variance = 0 
    variance_of_residuals = 0 
    regression = model["regression"]
    independent_array = model["independent_array"]
    dependent_array = model["dependent_array"]
    dependent_average = dependent_array.mean()
    yhats = apply_beta(regression, independent_array)

    for y, yhat in np.nditer([dependent_array, yhats]):
        variance += (y - dependent_average) ** 2
        variance_of_residuals += (y - yhat) ** 2

    r_squared = 1 - variance_of_residuals / variance

    return r_squared

def get_coefficient_of_determination(indicies, dependent, data):
    '''
    This function produces all models of one independent variables. 
    Inputs: 
        indicies: the indicies of the data
        dependent: the index of the dependent variable
        data: the training data
    Outputs:
        trained_models: a list of all models dictioanries
    '''
    trained_models = []
    for col_num in indicies:
        one_model = get_model([col_num], dependent, data)
        one_model["r_squared"] = get_variance(one_model)
        trained_models.append(one_model)
    return trained_models


def get_all_variables(indicies, dependent, data):
    '''
    This function produces one model using al independent variables
    Inputs: 
        indicies: the indicies of the data
        dependent: the index of the dependent variable
        data: the training data
    Outputs:
        one model: a list of the model using all independent variables
    '''
    one_model = get_model(indicies, dependent, data)
    one_model["r_squared"] = get_variance(one_model) 
    return [one_model]


def get_bivariate_models(indicies, dependent, data):
    '''
    This function builds a bivariate model and returns the highest R2 value 
    with the two variables used
    Inputs: 
        indicies: the indicies of the data
        dependent: the index of the dependent variable
        data: the training data
    Outputs:
        trained_models: a list of all models dictioanries
    '''
    trained_models = {"r_squared": 0}
    secondary_pair = indicies.copy()

    for first_variables in indicies:
        del secondary_pair[0]

        for second_variable in secondary_pair:
            one_model = get_model([first_variables, second_variable], dependent, data)
            one_model["r_squared"] = get_variance(one_model)       
            if one_model["r_squared"] > trained_models["r_squared"]:
                trained_models = one_model

    return [trained_models]
    

def get_greedy_algorithm(indicies, dependent, data):
    '''
    This function preforms the greedy algorithm on the training data.
    Inputs: 
        indicies: the indicies of the data
        dependent: the index of the dependent variable
        data: the training data
    Outputs:
        trained_models: a list of all models dictioanries
    '''
    trained_models = []
    remaining_variables = indicies[:]
    delete_index = 0
    # intialized with keys to prevent empty dictionary issues in 259 for first iteration
    best_model = {"indicies":[], "r_squared": 0}
    
    for i in range(len(remaining_variables)):
        best_current_model = {"indicies":[], "r_squared": 0}
        
        for position, variable in enumerate(remaining_variables):
            test_list = best_model["indicies"] + [variable]
            one_model = get_model(test_list, dependent, data)
            one_model["r_squared"] = get_variance(one_model)
            
            if one_model["r_squared"] > best_current_model["r_squared"]:
                best_current_model = one_model
                delete_index = position
        
        best_model = best_current_model
        del remaining_variables[delete_index]
        trained_models.append(best_model.copy())
    
    return trained_models


def get_greedy_threshold(indicies, dependent, data, threshold = 0):
    '''
    This function preforms the greedy algorithm with a threshold.
    Inputs: 
        indicies: the indicies of the data
        dependent: the index of the dependent variable
        data: the training data
    Outputs:
        previous_model: a list of the last model that satisfies the threshold condition
    '''
    remaining_variables = indicies[:]
    delete_index = 0
    # intialized with key to prevent empty dictionary issues in 293 for first iteration
    previous_model = {"indicies":[], "r_squared": 0}
    
    for i in range(len(remaining_variables)):
        best_current_model = {"indicies":[], "r_squared": 0}
        
        for position, variable in enumerate(remaining_variables):
            test_list = previous_model["indicies"] + [variable]
            one_model = get_model(test_list, dependent, data)
            one_model["r_squared"] = get_variance(one_model)

            if one_model["r_squared"] > best_current_model["r_squared"]:
                best_current_model = one_model
                delete_index = position

        if best_current_model["r_squared"] - previous_model["r_squared"] < threshold:
            return [previous_model]

        previous_model = best_current_model
        del remaining_variables[delete_index]

    return [previous_model]


def use_trained_model(trained_models, dependent, testing_data):
    '''
    This functions uses the models produced in task 3a to see if they are appropriate for 
    the testing data.
    Inputs: 
        trained_models: a list of the trained models 
        dependent: the index of the independent variable
        testing_data: the data that the model is being tested on
    Outputs:
        tested_model: a list of the tested models contianing new r_square values. 
    '''
    tested_models = []
    
    for tested_model in trained_models:
        tested_model["independent_array"] = testing_data[:, tested_model["indicies"]]
        tested_model["dependent_array"] = testing_data[:, dependent]
        tested_model["r_squared"] = get_variance(tested_model)
        tested_models.append(tested_model)
    
    return tested_models  

def go(name_of_data, var_indicies, dependent_index, col_names, training, testing_data):
    '''
    This function runs all of the functions that do task 1 to 4. Provides a simple call for the other 
    py files
    Inputs:
        name_of_data: Name of the Data City, Used for print heading
        var_indicies: the indicies of all independent variables
        dependent_index: the index of the dependent variable
        col_names: the column names and of the array
        training: the data that is used to train the model
        testing_data: the data is the used after a model is trained_model
    Outputs:
        None, This function strctly prints the outputs
    '''
    #Task 1.A
    task_1a = get_coefficient_of_determination(var_indicies, dependent_index, training)
    print("{} Task 1a".format(name_of_data))
    print_models(task_1a, col_names)

    #Task 1.B
    task_1b = get_all_variables(var_indicies, dependent_index, training)
    print("{} Task 1b".format(name_of_data))
    print_models(task_1b, col_names)

    #Task 2
    task_2 = get_bivariate_models(var_indicies, dependent_index, training)
    print("{} Task 2".format(name_of_data))
    print_models(task_2, col_names)

    #Task 3.A
    task_3a = get_greedy_algorithm(var_indicies, dependent_index, training)
    print("{} Task 3.A".format(name_of_data))
    print_models(task_3a, col_names)

    #Task 3.B
    task_3b = get_greedy_threshold(var_indicies, dependent_index, training, .1)
    print("{} Task 3.B with threshold of .1".format(name_of_data))
    print_models(task_3b, col_names)

    #Task 3.B
    task_3b = get_greedy_threshold(var_indicies, dependent_index, training, .01)
    print("{} Task 3.B with threshold of .01".format(name_of_data))
    print_models(task_3b, col_names)

    #Task 4
    print("{} Task 4".format(name_of_data))
    task_4 = use_trained_model(task_3a, dependent_index, testing_data)
    print_models(task_4, col_names)    