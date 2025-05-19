# main.py
import pandas as pd
import os
import json

from ad_boredom_analyzer import data_generator
from ad_boredom_analyzer import metrics
from ad_boredom_analyzer import model
from ad_boredom_analyzer import visualization
from ad_boredom_analyzer import config


def ensure_directories():
    if not os.path.exists(config.INPUT_DATA_DIR):
        os.makedirs(config.INPUT_DATA_DIR)
        print(f"Created directory: {config.INPUT_DATA_DIR}")
    if not os.path.exists(config.OUTPUT_DATA_DIR):
        os.makedirs(config.OUTPUT_DATA_DIR)
        print(f"Created directory: {config.OUTPUT_DATA_DIR}")


def run_full_analysis(input_csv_path: str = os.path.join(config.INPUT_DATA_DIR, config.DEFAULT_INPUT_FILENAME)):

    print(f"\n--- Starting Full Analysis on {input_csv_path} ---")

    try:
        raw_df = pd.read_csv(input_csv_path)
        print(f"Successfully loaded data from {input_csv_path}. Shape: {raw_df.shape}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_csv_path}.")
        print("Please generate data first (Option 1) or place the file in the 'data/' directory.")
        return
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    if raw_df.empty:
        print("Error: The input CSV file is empty.")
        return
    required_cols = ['user_id', 'ad_id', 'view_time', 'clicked', 'view_count', 'date']
    if not all(col in raw_df.columns for col in required_cols):
        print(f"Error: Input CSV must contain columns: {', '.join(required_cols)}")
        missing = [col for col in required_cols if col not in raw_df.columns]
        print(f"Missing columns: {', '.join(missing)}")
        return

    print("\nCalculating aggregated metrics...")
    try:
        aggregated_metrics_df = metrics.calculate_aggregated_metrics(raw_df)
        print("Aggregated metrics calculated.")
    except Exception as e:
        print(f"Error during metric calculation: {e}")
        return

    print("\nCalculating boredom scores...")
    try:
        boredom_df = metrics.calculate_boredom_score(
            aggregated_metrics_df,
            saturation_point=config.SATURATION_VIEW_COUNT
        )
        print("Boredom scores calculated.")
    except Exception as e:
        print(f"Error during boredom score calculation: {e}")
        return

    print("\nGetting recommendations...")
    try:
        recommendations_df = model.get_recommendations(
            boredom_df,
            threshold=config.BOREDOM_THRESHOLD
        )
        print("Recommendations generated.")
        print("Sample recommendations:\n", recommendations_df.head())
    except Exception as e:
        print(f"Error during recommendation generation: {e}")
        return

    output_csv_path = os.path.join(config.OUTPUT_DATA_DIR, config.RECOMMENDATIONS_CSV_FILENAME)
    output_json_path = os.path.join(config.OUTPUT_DATA_DIR, config.RECOMMENDATIONS_JSON_FILENAME)

    try:
        recommendations_df.to_csv(output_csv_path, index=False)
        print(f"\nRecommendations saved to CSV: {output_csv_path}")

        recommendations_df.to_json(output_json_path, orient="records", indent=4)
        print(f"Recommendations saved to JSON: {output_json_path}")
    except Exception as e:
        print(f"Error saving results: {e}")
        return

    print("\nGenerating visualizations...")
    try:
        visualization.plot_boredom_vs_views(
            recommendations_df,
            output_dir=config.OUTPUT_DATA_DIR,
            filename=config.BOREDOM_VS_VIEWS_PLOT_FILENAME
        )
        visualization.plot_boredom_distribution(
            recommendations_df,
            output_dir=config.OUTPUT_DATA_DIR,
            filename=config.BOREDOM_DISTRIBUTION_PLOT_FILENAME
        )
        print("Visualizations saved to 'output/' directory.")
    except Exception as e:
        print(f"Error during visualization: {e}")

    print("\n--- Full Analysis Complete ---")


def display_menu():
    print("\n========== Ad Boredom Analyzer ==========")
    print("1. Generate Sample Ad Interaction Data")
    print("2. Run Full Analysis (Load Data, Analyze, Recommend, Visualize)")
    print("3. View Configuration")
    print("4. Exit")
    print("========================================")
    choice = input("Enter your choice (1-4): ")
    return choice


def main():
    ensure_directories()

    while True:
        choice = display_menu()

        if choice == '1':
            try:
                num_records = int(input(
                    f"Enter number of records to generate (default {config.NUM_RECORDS_TO_GENERATE}): ") or config.NUM_RECORDS_TO_GENERATE)
                num_users = int(
                    input(f"Enter number of unique users (default {config.NUM_USERS}): ") or config.NUM_USERS)
                num_ads = int(input(f"Enter number of unique ads (default {config.NUM_ADS}): ") or config.NUM_ADS)
                output_filename = input(
                    f"Enter output filename (default {config.DEFAULT_INPUT_FILENAME}): ") or config.DEFAULT_INPUT_FILENAME

                data_generator.generate_ad_data(
                    num_records=num_records,
                    num_users=num_users,
                    num_ads=num_ads,
                    output_dir=config.INPUT_DATA_DIR,
                    filename=output_filename
                )
                print(f"Sample data generated in '{config.INPUT_DATA_DIR}/{output_filename}'")
            except ValueError:
                print("Invalid input. Please enter numbers for record counts.")
            except Exception as e:
                print(f"An error occurred during data generation: {e}")

        elif choice == '2':
            input_filename = input(
                f"Enter input CSV filename (default: {config.DEFAULT_INPUT_FILENAME}, located in '{config.INPUT_DATA_DIR}/'): ") or config.DEFAULT_INPUT_FILENAME
            input_csv_full_path = os.path.join(config.INPUT_DATA_DIR, input_filename)
            run_full_analysis(input_csv_path=input_csv_full_path)

        elif choice == '3':
            print("\n--- Current Configuration ---")
            print(f"Input Data Directory: {config.INPUT_DATA_DIR}")
            print(f"Output Data Directory: {config.OUTPUT_DATA_DIR}")
            print(f"Default Input Filename: {config.DEFAULT_INPUT_FILENAME}")
            print(f"Saturation View Count for Boredom: {config.SATURATION_VIEW_COUNT}")
            print(f"Boredom Threshold for 'hide' recommendation: {config.BOREDOM_THRESHOLD}")
            print("----------------------------")

        elif choice == '4':
            print("Exiting application. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()