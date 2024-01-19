# Video Quality Metrics

Перекодирование видео и расчёт показателей качества VQM: VMAF, SSIM, PSNR, MSSSIM

Консольная программа позволяет вычислять показатели качества для перекодированного видео относительно исходного, для этого используется:

  `python main.py -ntm -ovp original.mp4 -tvp recoded.mp4 -ssim -psnr -ssim`

Кроме того, программа позволяет перекодировать видео с помощью кодера x264 (H.264), x265 (H.265), libaom (AV1) или CRF и расчитать показатели качества для перекодированного видео. Для задания пресетов кодирования используется команда -p. Например:

  `python main.py -ovp original.mp4 -crf 18 19 -p veryfast -ssim -psnr`

После покадровой оценки метрик для видео создаётся json-файл со статистикой, txt-таблица и визуальное представление метрик в виде графиков.

Для ускоренной оценки показателей качества длинных видео предусмотрена обрезка видео: создаётся видеоряд, захватывая сегмент длиной X из исходного видео каждые y секунд. Например:

  `python main.py -ovp original.mp4 -crf 18 19 --interval 10 --clip-length 3`

# Документация

Для вызова документации в терминале: `python main.py -h`:

```
Пример использования : main.py [-h] [--av1-cpu-used <1-8>] [-cl <1-60>] [-crf <0-51> [<0-51> ...]] [-dp DECIMAL_PLACES]
                                [-e {x264,x265,libaom-av1}] [-i <1-600>] [-subsample SUBSAMPLE] [--n-threads N_THREADS] [-ntm]
                                [-o OUTPUT_FOLDER] -ovp ORIGINAL_VIDEO_PATH [-p <preset/s> [<preset/s> ...]] [-sc] [-psnr]
                                [-ssim] [-msssim] [-t SECONDS] [-tvp TRANSCODED_VIDEO_PATH] [-vf VIDEO_FILTERS]

Дополнительные аргументы:
  -h, --help            Документация

Аргументы кодирования:
  --av1-cpu-used <1-8>  Используется только если выбран кодер libaom-av1 (AV1). Установка соотношения качество/скорость
                        кодирования (default: 5)
                        
  -crf <0-51> [<0-51> ...]
                        Установка CRF значения
  -e {x264,x265,libaom-av1}, --video-encoder {x264,x265,libaom-av1}
                        Выбор кодировщика (default: x264)
  -p <preset/s> [<preset/s> ...], --preset <preset/s> [<preset/s> ...]
                        Установка пресетов (default: medium)

Аргументы для метрики VMAF:
  -subsample SUBSAMPLE  Устновка значения n-го кадра видео, для которого вычисляются метрики (default: 1)
  --n-threads N_THREADS
                        Установка количества потоков при расчёте VMAF

Аргументы режима обзора видео:
  -cl <1-60>, --clip-length <1-60>
                        При использовании обзорного режима каждый X секундный сегмент будет взят из
                        оригинального видео с интервалом --interval (default: 1)
  -i <1-600>, --interval <1-600>
                        

Основные аргументы:
  -dp DECIMAL_PLACES, --decimal-places DECIMAL_PLACES
                        Количество знаков после запятой при выводе данных в таблицу (default: 2)
  -ntm, --no-transcoding-mode
                        Включение режима без перекодирования. Используется для вычисления метрик видео, которое
                        уже было перекодировано.Необходимо указать путь к оригинальному и кодированному видео
                        с помощью -ovp и -tvp соответственно (default: False)
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        Используется, если необходимо указать имя выходной папки (default: None)
  -ovp ORIGINAL_VIDEO_PATH, --original-video-path ORIGINAL_VIDEO_PATH
                        Путь к оригинальному видео (default: None)
  -sc, --show-commands  Команды FFmpeg (default: False)
  -t SECONDS, --encode-length SECONDS
                        Создание короткого видео длиной x секунд. Оригинальное видео урезается до первых x секунд (default: None)
  -tvp TRANSCODED_VIDEO_PATH, --transcoded-video-path TRANSCODED_VIDEO_PATH
                        Путь к кодированному видео (default: None)
  -vf VIDEO_FILTERS, --video-filters VIDEO_FILTERS
                        Добавление FFmpeg фильтров. Пример: -vf bwdif=mode=0,crop=1920:800:0:140 (default: None)

Доступные метрики:
  -psnr, --calculate-psnr
                        Добавление расчёта PSNR-метрики в дополнении к VMAF (default: False)
  -ssim, --calculate-ssim
                        Добавление расчёта SSIM-метрики в дополнении к VMAF (default: False)
  -msssim, --calculate-msssim
                        Добавление расчёта MSSSIM-метрики в дополнении к VMAF (default: False)
```

# Requirements

1. Python **3.6+**
2. `pip install -r requirements.txt`
3. FFmpeg и FFprobe установлены и находятся в PATH. Сборка FFmpeg должна иметь фильтр libvmaf v2.1.1 (или выше). В зависимости от кодировщика, который будет использован, FFmpeg должен также иметь сборку с libx264, libx265 и libaom.

Проверка наличия libvmaf/libx264/libx265/libaom в сборке FFmpeg: `ffmpeg -buildconf`.

Необходимо наличие `--enable-libvmaf`, `--enable-libx265`, `--enable-libx264` и `--enable-libaom`.
