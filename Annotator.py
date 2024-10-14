rectangle: bool = input('Segment with rectangle? (y/n): ').lower() == 'y'

image: str = 'car.png'
annotation_image: str = '001'

if rectangle:
    from Segmentator_point import segment_using_mouse
    segment_using_mouse(image_path=f'images/{image}', annotated_image_name=annotation_image)

else:
    from Segmentator_rectangle import segment_using_rectangle
    segment_using_rectangle(image_path=f'images/{image}', annotated_image_name=annotation_image)