import os
import shutil


def take_small_target(target, src, prefix_word, step):
    if not os.path.exists(target):
        os.makedirs(target)

    files = sorted([f for f in os.listdir(src) if f.startswith(prefix_word)])

    for i, img_name in enumerate(files):
        if i % step == 0:
            shutil.copy(os.path.join(src, img_name), os.path.join(target, img_name))


target1 = "small_JPEGImages"
target2 = "small_Annotations"
src1 = "JPEGImages"
src2 = "Annotations"

prefix_word = ("mov_001_", "mov_002_", "mov_003_", "mov_004_", "mov_005_", "mov_006_", "mov_007_", "mov_008_")

take_small_target(target1, src1, prefix_word, 30)
take_small_target(target2, src2, prefix_word, 30)