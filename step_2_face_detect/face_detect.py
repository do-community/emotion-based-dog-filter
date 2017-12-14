"""Test for face detection.

Move your face around and a green box will identify your face.
With the test frame in focus, hit `q` to exit.
i.e., Typing `q` into your terminal will do nothing.
"""

import cv2


def main():
    cap = cv2.VideoCapture(0)

    # (NEW) initialize front face classifier
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # (NEW) Convert to black-and-white
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blackwhite = cv2.equalizeHist(gray)

        # (NEW) Detect faces
        rects = cascade.detectMultiScale(
            blackwhite, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        # (NEW) Add all bounding boxes to the image
        for x, y, w, h in rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
