import numpy as np
import cv2
import os
from tensorflow.keras.utils import to_categorical
from keras.models import Sequential 
from keras.layers import Convolution2D, MaxPooling2D, Flatten, Dense

# Load images and labels
images = []
image_labels  = []
directory = 'dataset'
list_of_files = os.listdir(directory)
for file in list_of_files:
    subfiles = os.listdir(os.path.join(directory, file))
    for sub in subfiles:
        path = os.path.join(directory, file, sub)
        img = cv2.imread(path)
        img = cv2.resize(img, (32, 32))
        images.append(img)
        image_labels.append(int(file))  # Assuming labels are class indices
    print(file)

X = np.array(images)
Y = np.array(image_labels)

# Normalize pixel values
X = X.astype('float32') / 255.0

# Convert labels to one-hot encoding
Y_one_hot = to_categorical(Y, num_classes=5)  # Assuming 5 classes

# Define the model
classifier = Sequential()
classifier.add(Convolution2D(32, 3, 3, input_shape=(32, 32, 3), activation='relu', padding='same'))
classifier.add(MaxPooling2D(pool_size=(2, 2)))

classifier.add(Convolution2D(64, 3, 3, activation='relu', padding='same'))
classifier.add(MaxPooling2D(pool_size=(2, 2)))

classifier.add(Flatten())
classifier.add(Dense(units=128, activation='relu'))
classifier.add(Dense(units=5, activation='softmax'))  # Assuming 5 classes

# Compile the model
classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
classifier.fit(X, Y_one_hot, batch_size=32, epochs=50)

# Save the model
classifier.save_weights('modeltrain.weights.h5')            
model_json = classifier.to_json()
with open("model/train.json", "w") as json_file:
    json_file.write(model_json)

print(classifier.summary())
