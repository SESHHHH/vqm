import json
import os

import matplotlib.pyplot as plt
import numpy as np

from utils import force_decimal_places, line, Logger, plot_graph, get_metrics_list

log = Logger("save_metrics")


def get_metrics_save_table(
    comparison_table,
    json_file_path,
    args,
    decimal_places,
    data_for_current_row,
    table,
    output_folder,
    time_taken,
    crf_or_preset=None,
):
    with open(json_file_path, "r") as f:
        file_contents = json.load(f)

    frames = file_contents["frames"]
    frame_numbers = [frame["frameNum"] for frame in frames]

    metric_lookup = {
        "VMAF": "vmaf",
        "PSNR": "psnr_y",
        "SSIM": "float_ssim",
        "MS-SSIM": "float_ms_ssim"
    }

    collected_scores = {}

    metrics_list = get_metrics_list(args)
    for metric_type in metrics_list:
        metric_key = metric_lookup[metric_type]
        if frames[0]["metrics"][metric_key]:

            metric_scores = [frame["metrics"][metric_key] for frame in frames]


            mean_score = force_decimal_places(np.mean(metric_scores), decimal_places)
            min_score = force_decimal_places(min(metric_scores), decimal_places)
            std_score = force_decimal_places(np.std(metric_scores), decimal_places)

            collected_scores[metric_type] = {
                "min": min_score,
                "std": std_score,
                "mean": mean_score
            }

            log.info(f"Creating {metric_type} graph...")
            plot_graph(
                f"{metric_type}\nn_subsample: {args.subsample}",
                "Frame Number",
                metric_type,
                frame_numbers,
                metric_scores,
                mean_score,
                os.path.join(output_folder, metric_type),
            )

            data_for_current_row.append(f"{min_score} | {std_score} | {mean_score}")

    if not args.no_transcoding_mode:
        data_for_current_row.insert(0, crf_or_preset)
        data_for_current_row.insert(1, time_taken)

    table.add_row(data_for_current_row)

    collected_metric_types = '/'.join(metrics_list)
    table_title = (
        f"{collected_metric_types} values are in the format: Min | Standard Deviation | Mean"
    )

    with open(comparison_table, "w") as f:
        f.write(f"{table_title}\n")
        f.write(table.get_string())

    log.info(f"{comparison_table} has been updated.")
    line()
    return float(collected_scores["VMAF"]["mean"])
