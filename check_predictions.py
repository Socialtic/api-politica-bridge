import re
from utils import read_csv, row_to_dict, search_by_name, write_csv
from sheets import sheet_reader

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"
CSV_FILES = ["v03_predictions", "v03_predictions_backfill"]


def main():
    pattern = "^PredictedFacebookUrl_[1-4]$"
    dataset = sheet_reader(SHEET_ID, "TODO!A1:AF2347")
    for csv_file in CSV_FILES:
        line = 'person_id,sheet_name,fb_name,fb_url_predict,score\n'
        predictions = read_csv(csv_file, "predictions")
        header = predictions.pop(0)
        predictions = [row_to_dict(row, header) for row in predictions]
        for prediction in predictions:
            if csv_file.endswith("backfill"):
                person_id, current_row = search_by_name(dataset,
                                                        prediction["figure_name"])
            else:
                person_id = int(prediction["figure_id"])
                current_row = dataset[person_id - 1]
                if current_row["full_name"] != prediction["figure_name"]:
                    person_id, current_row = search_by_name(dataset,
                                                            prediction["figure_name"])
            for field, url in prediction.items():
                if re.search(pattern, field) and url:
                    url = url.rstrip("/")
                    is_fb_page = url == current_row["URL_FB_page"]
                    is_fb_profile = url == current_row["URL_FB_profile"]
                    if is_fb_page or is_fb_profile:
                        continue
                    else:
                        line += f"{person_id},"
                        line += f"{current_row['full_name']},"
                        line += f"{prediction['figure_name']},"
                        line += f"{prediction[field]},"
                        score_key = f"PredictedFBScore_{field[-1]}"
                        line += f"{prediction[score_key]}\n"
        write_csv(line, f"predictions/{csv_file}_results")
    print("Finish!!")


if __name__ == "__main__":
    main()
