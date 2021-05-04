import re
from utils import read_csv, row_to_dict, search_by_name, write_csv
from sheets import sheet_reader

SHEET_ID = "1mk9LTI5RBYwrEPzILeDY925VJbLVmEoZyRzaa1gZ_hk"

def main():
    pattern = "^PredictedFacebookUrl_[1-4]$"
    line = 'person_id,sheet_name,fb_name,fb_url_predict,score\n'
    dataset = sheet_reader(SHEET_ID, "TODO!A1:AF2347")
    predictions = read_csv("v03_predictions.csv", "predictions")
    header = predictions.pop(0)
    predictions = [row_to_dict(row, header) for row in predictions]
    for prediction in predictions:
        try:
            person_id = int(prediction["figure_id"])
        except ValueError:
            breakpoint()
        current_row = dataset[person_id - 1]
        if current_row["full_name"] != prediction["figure_name"]:
            current_row = search_by_name(dataset, prediction["figure_name"])
        for field, url in prediction.items():
            if re.search(pattern, field) and url:
                url = url.rstrip("/")
                if url == current_row["URL_FB_page"] or url == current_row["URL_FB_profile"]:
                    continue
                else:
                    line += f"{person_id},"
                    line += f"{current_row['full_name']},"
                    line += f"{prediction['figure_name']},"
                    line += f"{prediction[field]},"
                    score_key = f"PredictedFBScore_{field[-1]}"
                    line += f"{prediction[score_key]}\n"
    write_csv(line, "predictions/results")
    print("Finish!!")


if __name__ == "__main__":
    main()
