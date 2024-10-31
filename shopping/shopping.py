import csv
import sys
import numpy as np
import datetime

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

def mystrtobool(text):
    return 1 if text == 'TRUE' else 0

def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    with open(filename) as file:
        reader = csv.reader(file)

        next(reader)
        for row in reader:
            row_evidence = list(np.zeros(17))

            for i in [0,2,4,11,12,13,14]:
                row_evidence[i] = int(row[i])

            for i in [1,3,5,6,7,8,9]:
                row_evidence[i] = float(row[i])
            
            row_evidence[10] = int(datetime.datetime.strptime(row[10][:3], "%b").month)-1
            row_evidence[15] = 1 if row[15]=='Returning_Visitor' else 0
            row_evidence[16] = mystrtobool(str(row[16]))
            
            labels.append(mystrtobool(row[-1]))
            evidence.append(row_evidence)
    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    return model.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    positive_total = len([item for item in labels if item==1])
    negative_total = len([item for item in labels if item==0])
    true_positive = 0
    true_negative = 0

    for ind_label, ind_predict in zip(labels, predictions):
        if ind_label==0 and ind_predict==0:
            true_negative+=1
        elif ind_label==1 and ind_predict==1:
            true_positive+=1
    return(true_positive/positive_total, true_negative/negative_total)


if __name__ == "__main__":
    main()