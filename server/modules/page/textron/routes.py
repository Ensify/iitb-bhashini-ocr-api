import uuid
from typing import List

import cv2
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse

from .dependencies import save_uploaded_images
from .models import *
from .helper import *
from ...config import *

router = APIRouter(
	prefix='/api/0.0.1/page/layout/text/word',
	tags=['Text Detection'],
)


@router.post('/', response_model=List[LayoutImageResponse])
async def layout_parser(
	folder_path: str = Depends(save_uploaded_images),
	model: ModelChoice = Form(ModelChoice.textron),
):
	"""
	API endpoint for calling the layout parser
	"""
	print(model.value)
	if model == ModelChoice.textron:
		ret = process_textron_output(folder_path)
	# if dilate:
	# 	ret = process_multiple_dilate(ret)
	return ret


@router.post('/visualize')
async def layout_parser_swagger_only_demo(
	image: UploadFile = File(...),
	model: ModelChoice = Form(ModelChoice.textron),
	dilate: bool = Form(False),
):
	"""
	This endpoint is only used to demonstration purposes.
	this endpoint returns/displays the input image with the
	bounding boxes clearly marked in blue rectangles.

	PS: This endpoint is not to be called from outside of swagger
	"""
	image_path = save_uploaded_image(image)
	if model == ModelChoice.textron:
		regions = textron_visualize(image_path)

	# if dilate:
	# 	regions = process_dilate(regions, image_path)
	save_location = '{}/{}.jpg'.format(
		IMAGE_FOLDER,str(uuid.uuid4())
	)
	# TODO: all the lines after this can be transfered to the helper.py file
	bboxes = [i.bounding_box for i in regions]
	bboxes = [((i.x, i.y), (i.x+i.w, i.y+i.h)) for i in bboxes]
	img = cv2.imread(image_path)
	count = 1
	for i in bboxes:
		img = cv2.rectangle(img, i[0], i[1], (0,0,255), 3)
		img = cv2.putText(
			img,
			str(count),
			(i[0][0]-5, i[0][1]-5),
			cv2.FONT_HERSHEY_COMPLEX,
			1,
			(0,0,255),
			1,
			cv2.LINE_AA
		)
		count += 1
	cv2.imwrite(save_location, img)
	return FileResponse(save_location)
