import json
import os
import textdistance
from collections import defaultdict

from pdf_extraction import extract_structured_output

def calculate_f1_score(predictions, ground_truth):
    """
    Calculate F1 score given ground truth and prediction lists
    
    Args:
        ground_truth (list): List containing ground truth values
        predictions (list): List containing predicted values
        
    Returns:
        float: F1 score between 0.0 and 1.0
    """
    if len(ground_truth) == 0 or len(predictions) == 0:
        return 0.0

    # Calculate true positives, false positives, false negatives
    true_positives = len(set(ground_truth) & set(predictions))
    false_positives = len(set(predictions) - set(ground_truth))
    false_negatives = len(set(ground_truth) - set(predictions))
    
    # Calculate precision and recall
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    # Calculate F1 score
    if precision + recall == 0:
        return 0.0
    f1_score = 2 * (precision * recall) / (precision + recall)
    
    return f1_score

def calculate_levenshtein_distance(prediction, ground_truth):
    """
    Calculate the Levenshtein distance between two strings
    
    Args:
        ground_truth (str): Ground truth string
        prediction (str): Predicted string
        
    Returns:
        int: Levenshtein distance between the strings
    """
    return textdistance.levenshtein(prediction, ground_truth)

def run_eval(data_dir, gt_dir):
    """
    Compare predictions against ground truth files and calculate metrics
    
    Args:
        data_dir (str): Directory containing raw pdf files
        gt_dir (str): Directory containing ground truth JSON files
        
    Returns:
        dict: Dictionary containing evaluation metrics
    """
    metrics = defaultdict(list)
    
    # breakpoint()
    # Iterate through ground truth files
    for gt_file in os.listdir(gt_dir):
        if not gt_file.endswith('.json'):
            continue
            
        # Load ground truth JSON
        with open(os.path.join(gt_dir, gt_file), 'r') as f:
            gt = json.load(f)
            
        # Load matching prediction
        predictions = extract_structured_output(os.path.join(data_dir, gt_file[:-5]+'.pdf'))

        # Calculate metrics for each field
        metrics['policy_number'].append(
            calculate_levenshtein_distance(predictions.number, gt['policyNumber']) / len(gt['policyNumber'])  # normalize the distance by length of ground truth string
        )
        
        metrics['start_date'].append(
            calculate_levenshtein_distance(predictions.start_date, gt['policyStartDate']) / len(gt['policyStartDate'])  # normalize the distance by length of ground truth string
        )
        
        metrics['end_date'].append(
            calculate_levenshtein_distance(predictions.end_date, gt['policyEndDate']) / len(gt['policyEndDate'])  # normalize the distance by length of ground truth string
        )

        metrics['premium'].append(
            abs(predictions.premium - gt['policyPremium']) / gt['policyPremium']
        )
        
        # Compare forms and endorsements
        pred_forms = [(f.form_number, f.form_title.lower()) for f in predictions.forms_and_endorsements]
        gt_forms = [(f['id'], f['description'].lower()) for f in gt['policyFormsandEndorsements']]
        
        metrics['forms'].append(
            calculate_f1_score(pred_forms, gt_forms)
        )

    print(metrics)

    # Calculate average metrics
    avg_metrics = {}
    for field, values in metrics.items():
        if values:
            avg_metrics[field] = sum(values) / len(values)
        else:
            avg_metrics[field] = 0.0


    # Print metrics in a tabular format
    print("\nEvaluation Metrics:")
    print("-" * 50)
    for metric, score in avg_metrics.items():
        # All scores are normalized between [0-1]
        # Format score as percentage with 2 decimal places
        formatted_score = f"{score*100:.2f}%"
        # if metric == 'premium' or metric == "forms":
        #     # Convert normalized premium and forms metrics to a percentage error
        #     formatted_score = f"{score*100:.2f}%"
        # else:
        #     # Other metrics are distance values
        #     formatted_score = f"{score:.2f}"
        if metric == "forms":
            print(f"F1 score (in %) {metric.replace('_',' ').title():<30}{formatted_score:>20}")
        else:
            print(f"Error rate (in %) {metric.replace('_',' ').title():<30}{formatted_score:>20}")
    print("-" * 50)

    return avg_metrics


def parse_args():
    """
    Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate insurance policy information extraction')
    parser.add_argument('--gt_dir', 
                       type=str,
                       required=True,
                       help='Directory containing ground truth JSON files')
    parser.add_argument('--data_dir',
                       type=str, 
                       required=True,
                       help='Directory containing raw PDF files')
    
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    # print(result)
    run_eval(args.data_dir, args.gt_dir)

if __name__=="__main__":
    main()
