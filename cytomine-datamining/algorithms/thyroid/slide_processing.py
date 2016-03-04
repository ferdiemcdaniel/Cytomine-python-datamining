import cv2
import numpy as np
from sldc import Segmenter, SLDCWorkflow


class SlideSegmenter(Segmenter):
    """
    A segmenter performing :
    - Color deconvolution (see :class:`ColorDeconvoluter`)
    - Static thresholding (identify cells)
    - Morphological closure (remove holes in cells)
    - Morphological opening (remove small objects)
    - Morphological closure (merge close objects)

    Format
    ------
    the given numpy.ndarrays are supposed to be RGB images :
    np_image.shape = (height, width, color=3) with values in the range
    [0, 255]

    Constructor parameters
    ----------------------
    color_deconvoluter : :class:`ColorDeconvoluter` instance
        The color deconvoluter performing the deconvolution
    threshold : int [0, 255] (default : 120)
        The threshold value. The higher, the more true/false positive
    struct_elem : binary numpy.ndarray (default : None)
        The structural element used for the morphological operations. If
        None, a default will be supplied
    nb_morph_iter : sequence of int (default [1,3,7])
        The number of iterations of each morphological operation.
            nb_morph_iter[0] : number of first closures
            nb_morph_iter[1] : number of openings
            nb_morph_iter[2] : number of second closures
    """

    def __init__(self, color_deconvoluter, threshold=120,
                 struct_elem=None, nb_morph_iter=None):
        self._color_deconvoluter = color_deconvoluter
        self._threshold = threshold
        self._struct_elem = struct_elem
        if self._struct_elem is None:
            self._struct_elem = np.array([[0, 0, 1, 1, 1, 0, 0],
                                          [0, 1, 1, 1, 1, 1, 0],
                                          [1, 1, 1, 1, 1, 1, 1],
                                          [1, 1, 1, 1, 1, 1, 1],
                                          [1, 1, 1, 1, 1, 1, 1],
                                          [0, 1, 1, 1, 1, 1, 0],
                                          [0, 0, 1, 1, 1, 0, 0], ],
                                         dtype=np.uint8)
        self._nb_morph_iter = [1, 3, 7] if nb_morph_iter is None else nb_morph_iter

    def segment(self, np_image):
        tmp_image = self._color_deconvoluter.transform(np_image)

        # Static thresholding on the gray image
        tmp_image = cv2.cvtColor(tmp_image, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(tmp_image, self._threshold, 255, cv2.THRESH_BINARY_INV)

        # Remove holes in cells in the binary image
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self._struct_elem, iterations=self._nb_morph_iter[0])

        # Remove small objects in the binary image
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, self._struct_elem, iterations=self._nb_morph_iter[1])

        # Union architectural paterns
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, self._struct_elem, iterations=self._nb_morph_iter[2])

        return binary



