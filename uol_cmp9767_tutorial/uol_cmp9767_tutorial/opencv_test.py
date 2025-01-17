import rclpy
import cv2
import numpy as np
from rclpy.node import Node
from rclpy import qos
from cv2 import namedWindow, cvtColor, imshow, inRange

from cv2 import destroyAllWindows, startWindowThread
from cv2 import COLOR_BGR2GRAY, waitKey
from cv2 import blur, Canny, resize, INTER_CUBIC
from numpy import mean
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

font = cv2.FONT_HERSHEY_SIMPLEX

class ImageConverter(Node):

    def __init__(self):
        super().__init__('opencv_test')
        self.bridge = CvBridge()
        self.image_sub = self.create_subscription(Image, 
                                                    "/limo/depth_camera_link/image_raw",
                                                    self.image_callback,
                                                    qos_profile=qos.qos_profile_sensor_data) # Set QoS Profile
        
        
    def image_callback(self, data):
        namedWindow("Image window")
        namedWindow("Masked")

        cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        cv_image = resize(cv_image, None, fx=1, fy=1, interpolation = INTER_CUBIC)

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        lower_pink = np.array([140, 50, 150])
        upper_pink = np.array([180, 255, 255])

        mask = cv2.inRange(hsv, lower_pink, upper_pink)

        def search_contours(mask):
            contours_count = 0
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                cv2.drawContours(cv_image, [contour], -1, (0, 255, 0), 2)
                contours_count += 1

                M = cv2.moments(contour)
                if M["m00"] !=0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0
                cv2.putText(cv_image, f"{contours_count}", (cX - 25, cY -25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            return contours_count

        count = search_contours(mask)

        imshow("Image window", cv_image)
        imshow("Masked", mask)

        waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    image_converter = ImageConverter()
    rclpy.spin(image_converter)

    image_converter.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()