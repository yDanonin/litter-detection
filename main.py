import cv2
import numpy as np

# Load the image
image = cv2.imread('datasets\TACO\data\\batch_2\\000016.JPG')

# Resize the image while maintaining aspect ratio
max_dimension = 720  # Set a maximum size for the largest dimension
height, width = image.shape[:2]

# Calculate scaling factor
scaling_factor = max_dimension / float(max(height, width))

# Resize the image with the calculated scaling factor
new_width = int(width * scaling_factor)
new_height = int(height * scaling_factor)
resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

# Convert to HSV color space for color filtering
hsv = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)

# Define color range for filtering (example: bright colors)
lower_color = np.array([0, 50, 50])
upper_color = np.array([50, 255, 255])
mask = cv2.inRange(hsv, lower_color, upper_color)

# Apply Gaussian Blur to the mask
blurred_mask = cv2.GaussianBlur(hsv, (7, 7), 0)

edges = cv2.Canny(blurred_mask, 50, 150)

# Apply morphological operations to clean up the edges
kernel = np.ones((3, 3), np.uint8)
edges_cleaned = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)  # Close gaps in edges

# Find contours
contours, _ = cv2.findContours(edges_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw bounding boxes around filtered contours
for contour in contours:
    # Filter based on contour area
    area = cv2.contourArea(contour)
    if 500 < area < 5000:  # Adjust area limits as needed
        # Calculate bounding box
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if 0.5 < aspect_ratio < 2.0:  # Filter based on aspect ratio
            cv2.rectangle(resized_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Show the final image with detected litter
#cv2.imshow('Enhanced Litter Detection', resized_image)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

################################################################
# Function to ensure the image is 3-channel (BGR)
def ensure_bgr(image):
    if len(image.shape) == 2 or image.shape[2] == 1:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image

# Function to add subtitle to an image with background color
def add_subtitle(image, text):
    # Define the font, scale, color, and thickness
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_color = (255, 255, 255)  # White color
    font_thickness = 2
    background_color = (0, 0, 0)  # Black background

    # Calculate text size
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_width, text_height = text_size

    # Calculate position for the text
    text_x = (image.shape[1] - text_width) // 2
    text_y = image.shape[0] - 10

    # Draw background rectangle
    rectangle_start = (text_x - 5, text_y - text_height - 5)
    rectangle_end = (text_x + text_width + 5, text_y + 5)
    cv2.rectangle(image, rectangle_start, rectangle_end, background_color, cv2.FILLED)

    # Put the text on the image
    cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

# Convert single-channel images to 3-channel for display purposes
mask_bgr = ensure_bgr(mask)
blurred_mask_bgr = ensure_bgr(blurred_mask)
edges_cleaned_bgr = ensure_bgr(edges_cleaned)

# Add subtitles to each image
add_subtitle(resized_image, 'Resized Image')
add_subtitle(hsv, 'HSV Image')
add_subtitle(mask_bgr, 'Mask')
add_subtitle(blurred_mask_bgr, 'Blurred Mask')
add_subtitle(edges_cleaned_bgr, 'Edges Cleaned')

# Stack all images horizontally
top_row = np.hstack((resized_image, hsv))
bottom_row = np.hstack((mask_bgr, blurred_mask_bgr, edges_cleaned_bgr))

# Adjust the sizes to match (if necessary)
if top_row.shape[1] != bottom_row.shape[1]:
    bottom_row = cv2.resize(bottom_row, (top_row.shape[1], bottom_row.shape[0]))

# Combine top and bottom rows vertically
combined_image = np.vstack((top_row, bottom_row))

# Allow the window to be resizable
cv2.namedWindow('All Steps Combined', cv2.WINDOW_NORMAL)

# Show the combined image
cv2.imshow('All Steps Combined', combined_image)

# Wait for key press and close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
