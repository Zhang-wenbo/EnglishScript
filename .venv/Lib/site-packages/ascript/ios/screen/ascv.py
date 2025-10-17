import os
import cv2
import numpy as np
from typing import Union




def find_all_template_cvimg(image_source, image_search: Union[np.ndarray, list], rect: list = None, threshold=0.5,
                            rgb=False,
                            maxcnt=0):
    if image_search is None:
        return None

    """模版匹配"""
    # 处理主图 颜色通道
    if not rgb:
        image_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2GRAY)
    else:
        image_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2HSV)
        source_h, source_s, source_v = cv2.split(image_source)
        image_hs = cv2.merge([source_h, source_s])

    # 处理主图 的范围大小
    source_height, source_width = image_source.shape[:2]

    x, y = [0, 0]
    if rect:
        # 这里只做坐标偏移
        x, y, r, b = rect

    image_search_list = []
    if isinstance(image_search, list):
        image_search_list = image_search

    else:
        image_search_list.append(image_search)

    result = []
    method = cv2.TM_CCOEFF_NORMED
    for image_cv in image_search_list:
        res = None
        # print("stp 1")
        # if not os.path.isfile(image_search_path):
        #     raise RuntimeError(f"文件不存在{image_search_path}")
        w, h = image_cv.shape[1], image_cv.shape[0]
        if not rgb:
            # image_search = cv2.imread(image_search_path, cv2.IMREAD_GRAYSCALE)
            # w, h = image_search.shape[1], image_search.shape[0]
            image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            if source_width > w and source_height > h:
                res = cv2.matchTemplate(image_source, image_cv, method)
        else:
            # 分别计算3通道的rgb值
            # image_search = cv2.imread(image_search_path)
            search_hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)
            search_h, search_s, search_v = cv2.split(search_hsv)
            search_hs = cv2.merge([search_h, search_s])
            if source_width > w and source_height > h:
                res = cv2.matchTemplate(image_hs, search_hs, cv2.TM_CCOEFF_NORMED)
            # res = resbgr[2]

        # print("stp 2")

        while True and res is not None:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            if max_val < threshold:
                break

            # calculator middle point
            # 把 范围 x,y 偏移加进去
            top_left = [a + b for a, b in zip(max_loc, [x, y])]
            middle_point = (top_left[0] + w / 2, top_left[1] + h / 2)
            result.append(dict(
                result=middle_point,
                rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]),
                           (top_left[0] + w, top_left[1] + h)),
                rect=[top_left[0], top_left[1], top_left[0] + w, top_left[1] + h],
                center_x=int(middle_point[0]),
                center_y=int(middle_point[1]),
                confidence=max_val
            ))
            if maxcnt and len(result) >= maxcnt:
                break
            # floodfill the already found area
            cv2.floodFill(res, None, max_loc, (-1000,), max_val - threshold + 0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)

        # print("stp 3")
    return result


def find_all_template(image_source, image_search: Union[str, list], rect: tuple = None, threshold=0.5, rgb=False,
                      maxcnt=0, bgremove=False):
    if image_search is None:
        return None

    """模版匹配"""
    # 处理主图 颜色通道
    if not rgb:
        image_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2GRAY)
    else:
        image_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2HSV)
        source_h, source_s, source_v = cv2.split(image_source)
        image_hs = cv2.merge([source_h, source_s])
        # 处理主图 的范围大小

    source_height, source_width = image_source.shape[:2]

    x, y = [0, 0]
    if rect:
        # 这里只做坐标偏移
        x, y, r, b = rect

    image_search_list = []
    if isinstance(image_search, list):
        image_search_list = image_search
    else:
        image_search_list.append(image_search)
    result = []
    method = cv2.TM_CCOEFF_NORMED
    for image_search_path in image_search_list:

        res = None

        if not os.path.isfile(image_search_path):
            raise RuntimeError(f"文件不存在{image_search_path}")

        if not rgb:
            image_search = cv2.imread(image_search_path, cv2.IMREAD_GRAYSCALE)
            w, h = image_search.shape[1], image_search.shape[0]
            if source_width > w and source_height > h:
                res = cv2.matchTemplate(image_source, image_search, method)
        else:
            # 分别计算3通道的rgb值
            image_search = cv2.imread(image_search_path)
            w, h = image_search.shape[1], image_search.shape[0]
            search_hsv = cv2.cvtColor(image_search, cv2.COLOR_BGR2HSV)
            search_h, search_s, search_v = cv2.split(search_hsv)
            search_hs = cv2.merge([search_h, search_s])
            if source_width > w and source_height > h:
                res = cv2.matchTemplate(image_hs, search_hs, cv2.TM_CCOEFF_NORMED)
            # res = resbgr[2]

        # print(res)

        while True and res is not None:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            if max_val < threshold:
                break

            # calculator middle point
            # 把 范围 x,y 偏移加进去
            top_left = [a + b for a, b in zip(max_loc, [x, y])]
            middle_point = (top_left[0] + w / 2, top_left[1] + h / 2)
            result.append(dict(
                result=middle_point,
                rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]),
                           (top_left[0] + w, top_left[1] + h)),
                rect=[top_left[0], top_left[1], top_left[0] + w, top_left[1] + h],
                center_x=int(middle_point[0]),
                center_y=int(middle_point[1]),
                confidence=max_val
            ))
            if maxcnt and len(result) >= maxcnt:
                break
            # floodfill the already found area
            cv2.floodFill(res, None, max_loc, (-1000,), max_val - threshold + 0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
    return result


surf = None
sift = None


def find_surf(image_source, image_search: Union[str, list], threshold=0.5, off_rect: tuple = None, rgb: bool = False,
              maxcnt: int = 0):
    # 读取图片
    if not rgb:
        image_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2GRAY)
    # 初始化SURF检测器
    global surf
    if surf is None:
        surf = cv2.xfeatures2d.SURF_create()

    result = []
    mask_source = image_source.copy()

    image_search_list = []
    if isinstance(image_search, list):
        image_search_list = image_search
    else:
        image_search_list.append(image_search)

    for image_search_path in image_search_list:
        if not os.path.isfile(image_search_path):
            raise RuntimeError(f"文件不存在{image_search_path}")

        # raise RuntimeError(f"文件地址{image_search_path}")
        small_image = None
        if rgb:
            small_image = cv2.imread(image_search_path)
        else:
            small_image = cv2.imread(image_search_path, cv2.IMREAD_GRAYSCALE)

        while len(result) < maxcnt or maxcnt == 0:
            if small_image is None:
                break

            try:
                # 找到关键点和描述符
                keypoints_large, descriptors_large = surf.detectAndCompute(mask_source, None)
                keypoints_small, descriptors_small = surf.detectAndCompute(small_image, None)
                # 使用FLANN matcher进行匹配
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)
                flann = cv2.FlannBasedMatcher(index_params, search_params)

                if descriptors_large is None or descriptors_small is None:
                    break

                if descriptors_large.shape[0] < 2:
                    break

                matches = flann.knnMatch(descriptors_small, descriptors_large, k=2)
                # 应用比率测试
                good_matches = []
                for m, n in matches:
                    if m.distance < 0.8 * n.distance:
                        good_matches.append(m)

                # 如果有足够的匹配点，则计算仿射变换矩阵
                if len(good_matches) > 4:
                    src_pts = np.float32([keypoints_small[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([keypoints_large[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                    # 计算仿射变换矩阵
                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    matches_mask = mask.ravel().tolist()
                    confidence = min(1.0 * matches_mask.count(1) / 10, 1.0)

                    if confidence < threshold:
                        break

                    # 使用仿射变换矩阵找到小图在大图中的位置
                    height, width = small_image.shape
                    pts = np.float32([[0, 0], [0, height - 1], [width - 1, height - 1], [width - 1, 0]]).reshape(-1, 1,
                                                                                                                 2)
                    dst = cv2.perspectiveTransform(pts, M)

                    # 计算小图在大图中的位置
                    x, y, w, h = cv2.boundingRect(np.int0(dst))
                    # 增加掩膜
                    cv2.rectangle(mask_source, (x, y), (x + w, y + h), 255, -1)  # -1 表示填充整个矩形
                    if off_rect:
                        # print(off_rect, x, y, w, h)
                        x = x + off_rect[0]
                        y = y + off_rect[1]
                    middle_point = (x + w / 2, y + h / 2)
                    result.append(dict(
                        result=middle_point,
                        rectangle=[(x, y), (x, y + h), (x + w, y), (x + w, y + h)],
                        rect=[x, y, x + w, y + h],
                        center_x=int(middle_point[0]),
                        center_y=int(middle_point[1]),
                        confidence=confidence
                    ))

                    if len(result) > 20:
                        break
                else:
                    # 如果没有足够的匹配点，返回None
                    # print("-none")
                    break
            except RuntimeError:
                break

        del small_image

    del mask_source
    del image_source

    return result


def find_sift(image_source, image_search: Union[str, list], threshold=0.5, off_rect: tuple = None, rgb: bool = False,
              maxcnt: int = 0 ):
    # 读取图片
    if not rgb:
        image_source = cv2.cvtColor(image_source, cv2.COLOR_BGR2GRAY)
    # 初始化SURF检测器
    global sift
    if sift is None:
        # 创建一个sift 算法识别器,参数默认这样写.可以百度啥意思. 这个算法必须在最新的python 去创建,否则商业版权原因没有包含进去
        sift = cv2.SIFT.create(nfeatures=0, nOctaveLayers=3, contrastThreshold=0.04, edgeThreshold=10, sigma=1.6)

    result = []
    mask_source = image_source.copy()

    image_search_list = []
    if isinstance(image_search, list):
        image_search_list = image_search
    else:
        image_search_list.append(image_search)

    for image_search_path in image_search_list:
        if not os.path.isfile(image_search_path):
            raise RuntimeError(f"文件不存在{image_search_path}")

        # raise RuntimeError(f"文件地址{image_search_path}")
        small_image = None
        if rgb:
            small_image = cv2.imread(image_search_path)
        else:
            small_image = cv2.imread(image_search_path, cv2.IMREAD_GRAYSCALE)

        # 这里看 查询到的结果数量要小于 参数里的结果数量, 或者 =0 的时候一直查找.
        while len(result) < maxcnt or maxcnt == 0:
            if small_image is None:
                break

            try:
                # 找到大图和小图的关键点和描述符
                keypoints_large, descriptors_large = sift.detectAndCompute(mask_source, None)
                keypoints_small, descriptors_small = sift.detectAndCompute(small_image, None)
                # 使用FLANN matcher进行匹配
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)
                flann = cv2.FlannBasedMatcher(index_params, search_params)

                if descriptors_large is None or descriptors_small is None:
                    break

                if descriptors_large.shape[0] < 2:
                    break

                # 使用 flann 去匹配特征点
                matches = flann.knnMatch(descriptors_small, descriptors_large, k=2)
                # 应用比率测试
                good_matches = []
                for m, n in matches:
                    # 特征点比对
                    if m.distance < 0.8 * n.distance:
                        good_matches.append(m)

                # 如果有足够的匹配点，则计算仿射变换矩阵,来计算得到 小图在大图中的位置. 这里因为是不同分辨率,所以 得用这个方法
                if len(good_matches) > 4:
                    src_pts = np.float32([keypoints_small[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                    dst_pts = np.float32([keypoints_large[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                    # 计算仿射变换矩阵
                    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                    matches_mask = mask.ravel().tolist()
                    confidence = min(1.0 * matches_mask.count(1) / 10, 1.0)

                    if confidence < threshold:
                        break

                    # 使用仿射变换矩阵找到小图在大图中的位置
                    print(small_image.shape)
                    height, width = small_image.shape[:2]
                    pts = np.float32([[0, 0], [0, height - 1], [width - 1, height - 1], [width - 1, 0]]).reshape(-1, 1,
                                                                                                                 2)
                    dst = cv2.perspectiveTransform(pts, M)

                    # 计算小图在大图中的位置
                    x, y, w, h = cv2.boundingRect(np.int32(dst))
                    # 增加掩膜,大概意思,就是找到的位置扣掉.已方便循环查找其他点位
                    cv2.rectangle(mask_source, (x, y), (x + w, y + h), 255, -1)  # -1 表示填充整个矩形
                    if off_rect:
                        # print(off_rect, x, y, w, h)
                        x = x + off_rect[0]
                        y = y + off_rect[1]
                    middle_point = (x + w / 2, y + h / 2)
                    # 往结果集里添加 结果
                    result.append(dict(
                        result=middle_point,
                        rectangle=[(x, y), (x, y + h), (x + w, y), (x + w, y + h)],
                        rect=[x, y, x + w, y + h],
                        center_x=int(middle_point[0]),
                        center_y=int(middle_point[1]),
                        confidence=confidence
                    ))

                    if len(result) > 20:
                        break
                else:
                    # 如果没有足够的匹配点，返回None
                    # print("-none")
                    break
            except RuntimeError:
                break

        del small_image

    del mask_source
    del image_source
    return result


def compare_histograms(hist1, hist2, method=cv2.HISTCMP_CORREL):
    """比较两个直方图"""
    return cv2.compareHist(hist1, hist2, method)


def calc_histogram(image, mask=None, channels=[0, 1, 2]):
    """计算图像的直方图"""
    # print(image.shape[2])
    hist = cv2.calcHist([image], channels, mask, [256, 256, 256], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return hist.flatten()
