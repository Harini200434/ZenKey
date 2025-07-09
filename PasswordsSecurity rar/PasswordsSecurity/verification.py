
import os
import cv2

def fingerprint_Matching(fp1,fp2):
    status=False
    fingerprint_img = cv2.imread(fp1)

    fingerprint_img2 = cv2.imread(fp2)


    sift =cv2.SIFT_create()
    keypoints_1, des1 = sift.detectAndCompute(fingerprint_img, None)
    keypoints_2, des2 = sift.detectAndCompute(fingerprint_img2, None)
    #print(keypoints_1, des1)
    #print(keypoints_2, des2)

    matches = cv2.FlannBasedMatcher({"algorithm": 1, "trees": 1}, {}).knnMatch(
        des1, des2, k=2
    )

    for p, q in matches:
        if p.distance < 0.1 * q.distance:
            print("match")
            status=True

    return status


#fingerprint_Matching()