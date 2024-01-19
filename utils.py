import logging
import math
import numpy as np
import os
from pathlib import Path
import sys
from time import time

from ffmpeg import probe
import matplotlib.pyplot as plt
from tqdm import tqdm


class Logger:
    def __init__(self, name, filename="logs.log", print_to_terminal=True):
        with open(filename, "w"):
            pass

        logger = logging.getLogger(name)
        logger.setLevel(10)

        file_handler = logging.FileHandler(filename)
        logger.addHandler(file_handler)
        self._file_handler = file_handler

        if print_to_terminal:
            logger.addHandler(logging.StreamHandler())

        self._logger = logger

    def info(self, msg):
        self._file_handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
        self._logger.info(msg)

    def warning(self, msg):
        self._file_handler.setFormatter(logging.Formatter("[%(name)s] [WARNING] %(message)s"))
        self._logger.warning(msg)

    def debug(self, msg):
        self._file_handler.setFormatter(logging.Formatter("[%(name)s] [DEBUG] %(message)s"))
        self._logger.debug(msg)


class Timer:
    def start(self):
        self._start_time = time()

    def stop(self, decimal_places):
        time_to_convert = time() - self._start_time
        time_rounded = force_decimal_places(round(time_to_convert, decimal_places), decimal_places)
        return time_rounded


class VideoInfoProvider:
    def __init__(self, video_path):
        self._video_path = video_path

    def get_bitrate(self, decimal_places, video_path=None):
        if video_path:
            bitrate = probe(video_path)["format"]["bit_rate"]
        else:
            bitrate = probe(self._video_path)["format"]["bit_rate"]
        return f"{force_decimal_places((int(bitrate) / 1_000_000), decimal_places)} Mbps"

    def get_framerate_fraction(self):
        r_frame_rate = [
            stream
            for stream in probe(self._video_path)["streams"]
            if stream["codec_type"] == "video"
        ][0]["r_frame_rate"]
        return r_frame_rate

    def get_framerate_float(self):
        numerator, denominator = self.get_framerate_fraction().split("/")
        return int(numerator) / int(denominator)

    def get_duration(self):
        return float(probe(self._video_path)["format"]["duration"])


log = Logger("utils")


def cut_video(filename, args, output_ext, output_folder, comparison_table):
    cut_version_filename = f"{Path(filename).stem} [{args.encode_length}s]{output_ext}"

    output_file_path = os.path.join(output_folder, cut_version_filename)

    log.info(f"Cutting the video to a length of {args.encode_length} seconds...")
    os.system(
        f"ffmpeg -loglevel warning -y -i {args.original_video_path} -t {args.encode_length} "
        f'-map 0 -c copy "{output_file_path}"'
    )
    log.info("Done!")

    time_message = (
        f" for {args.encode_length} seconds" if int(args.encode_length) > 1 else "for 1 second"
    )

    with open(comparison_table, "w") as f:
        f.write(f"You chose to encode {filename}{time_message} using {args.video_encoder}.")

    return output_file_path


def exit_program(message):
    line()
    log.info(f"{message}\nThis program will now exit.")
    line()
    sys.exit()


def force_decimal_places(value, decimal_places):
    return f"{value:.{decimal_places}f}"


def is_list(argument_object):
    return isinstance(argument_object, list)


def line():
    width, height = os.get_terminal_size()
    log.info("-" * width)


def plot_graph(
    title, x_label, y_label, x_values, y_values, mean_y_value, save_path, bar_graph=False
):
    plt.suptitle(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if bar_graph:
        xlocs = x_values
        rotation = 0

        if isinstance(x_values[0], str):
            xlocs = np.arange(len(x_values))
            xticks_labels_rotation = 45
        else:
            xlocs = x_values
            xticks_labels_rotation = 0

        plt.xticks(xlocs, x_values, rotation=xticks_labels_rotation)
        plt.ylim(min(y_values) - 1, math.ceil(max(y_values)))

        i = 0
        for value in x_values:
            plt.bar(value, y_values[i], label=y_values[i])
            i += 1

        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.tight_layout()

    else:
        plt.plot(x_values, y_values, label=f"{y_label} ({mean_y_value})")
        plt.legend(loc="lower right")

    plt.savefig(save_path)
    plt.clf()


def show_progress_bar(ffmpeg_process, total_frames):
    progress_bar = tqdm(
            total=total_frames,
            unit=" frames",
            dynamic_ncols=True,
    )

    progress_bar.clear()
    previous_frame_number = 0

    try:
        while ffmpeg_process.poll() is None:
            line = ffmpeg_process.stdout.readline().decode("utf-8")
            if "frame=" in line:
                frame_number = int(line[6:])
                frame_number_increase = frame_number - previous_frame_number
                progress_bar.update(frame_number_increase)
                previous_frame_number = frame_number
    except KeyboardInterrupt:
        progress_bar.close()
        ffmpeg_process.kill()
        log.info("[KeyboardInterrupt] FFmpeg process killed. Exiting Video Quality Metrics.")
        sys.exit(0)


def write_table_info(table_path, video_filename, original_bitrate, args, crf_or_preset):
    with open(table_path, "a") as f:
        f.write(
            f"\nFile Transcoded: {video_filename}\n"
            f"Bitrate: {original_bitrate}\n"
            f"Encoder used for the transcodes: {args.video_encoder}\n"
            f"{crf_or_preset} was used.\n"
            f'Filter(s) used: {"None" if not args.video_filters else args.video_filters}\n'
            f"n_subsample: {args.subsample}"
        )

def get_metrics_list(args):
    metrics_list = [
        "VMAF",
        "PSNR" if args.calculate_psnr else None,
        "SSIM" if args.calculate_ssim else None,
        "MS-SSIM" if args.calculate_msssim else None
    ]

    return list(filter(None, metrics_list))
