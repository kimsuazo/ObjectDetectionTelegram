import numpy as np
import os
import PIL
import PIL.Image
import tensorflow as tf
import pathlib
import matplotlib.pyplot as plt


"""

def imshow(inp, title=None):
    
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(10)  # pause a bit so that plots are updated
    

"""


if __name__ == '__main__':

	#Define some parameters of the data
	batch_size = 32
	img_height = 180
	img_width = 180

	#Define the path
	path = "../images"
	data_dir = pathlib.Path(path)

	#Create training dataset from directory
	train_ds = tf.keras.preprocessing.image_dataset_from_directory(
	  data_dir,
	  validation_split=0.2,
	  subset="training",
	  seed=123,
	  image_size=(img_height, img_width),
	  batch_size=batch_size)

	#Create validation dataset from directory
	val_ds = tf.keras.preprocessing.image_dataset_from_directory(
	  data_dir,
	  validation_split=0.2,
	  subset="validation",
	  seed=123,
	  image_size=(img_height, img_width),
	  batch_size=batch_size)

	#Print the classes
	class_names = train_ds.class_names
	num_classes= len(class_names)

	#Check how the imputs are
	for image_batch, labels_batch in train_ds:
	  print(image_batch.shape)
	  print(labels_batch.shape)
	  break

	"""
	normalization_layer = tf.keras.layers.experimental.preprocessing.Rescaling(1./255)

	normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
	image_batch, labels_batch = next(iter(normalized_ds))
	first_image = image_batch[0]
	# Notice the pixels values are now in `[0,1]`.
	print(np.min(first_image), np.max(first_image))
	"""

	AUTOTUNE = tf.data.AUTOTUNE

	train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
	val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

	model = tf.keras.Sequential([
	  tf.keras.layers.experimental.preprocessing.Rescaling(1./255),
	  tf.keras.layers.Conv2D(32, 3, activation='relu'),
	  tf.keras.layers.MaxPooling2D(),
	  tf.keras.layers.Conv2D(32, 3, activation='relu'),
	  tf.keras.layers.MaxPooling2D(),
	  tf.keras.layers.Conv2D(32, 3, activation='relu'),
	  tf.keras.layers.MaxPooling2D(),
	  tf.keras.layers.Flatten(),
	  tf.keras.layers.Dense(128, activation='relu'),
	  tf.keras.layers.Dense(num_classes)
	])

	model.compile(
	  optimizer='adam',
	  loss=tf.losses.SparseCategoricalCrossentropy(from_logits=True),
	  metrics=['accuracy'])

	model.fit(
	  train_ds,
	  validation_data=val_ds,
	  epochs=3
	)