import torch
import numpy as np
import matplotlib.pyplot as plt
import cv2
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

#Show annotations on images
def show_anns(anns) -> None:
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)



sam_checkpoint: str ="./sam_vit_b_01ec64.pth"
model_type: str ="vit_b"

device: str = "cuda" if torch.cuda.is_available() else "cpu"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator=SamAutomaticMaskGenerator(model=sam,
                                        points_per_side=20,
                                        pred_iou_thresh=0.95,
                                        stability_score_thresh=0.95,
                                        stability_score_offset= 0.9,
                                        box_nms_thresh= 0.9,
                                        crop_n_points_downscale_factor=2,
                                        min_mask_region_area=200)

image_path: str ="./images/dogs.jpg"
image = cv2.imread(image_path)

masks = mask_generator.generate(image=image)

print(len(masks))
print(masks[0].keys())

plt.figure(figsize=(20,20))
plt.imshow(image)
show_anns(masks)
plt.axis('off')
plt.show() 