
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Input, Dense, Flatten, Dropout, BatchNormalization, Reshape, GlobalAveragePooling2D
from tensorflow.keras.utils import plot_model
from tensorflow.keras.applications import VGG19, VGG16



from preprocessing import *
from model_tuners import Callbacks

data_preprocessor = Preprocessing()
callback = Callbacks(monitor = 'val_loss' , patience = 2)
data_preprocessor.basic_descriptive_of_images()
train_image_aug, test_image_aug = data_preprocessor.data_augmentation()

train_set, test_set = data_preprocessor.dataset_splitting(train_image_aug, test_image_aug)


def model_create_and_train(model_type,):
    '''
    argument: model_type (which is going to be the type of Vgg model to work on either VGG19 or VGG 16)
    purpose: Create VGG model with necessary hyperparameters
    return: Created,compiled and trained Vgg model
    '''
    if model_type == 'VGG19':
        model_name = VGG19
    elif model_type == 'VGG16':
        model_name = VGG16
    else:
        return f'Error on Model type'
        quit()

    model = model_name(
        weights = 'imagenet',
        include_top = False,
        # input_shape = (224, 224, 3)
    )
    for layer in model.layers:
        layer.trainable = False
    
    x  = Flatten()(model.output)
    # Add a fully connected layer with 512 hidden units and ReLU activation
    x = Dense(512, activation='relu')(x)

    # Add a dropout rate of 0.5
    x = Dropout(0.5)(x)

    # Add a final sigmoid layer with 1 node for classification output
    x = Dense(1, activation='sigmoid')(x)
    predictions = Dense(1, activation='sigmoid')(x)

    model_final = Model(inputs=model.input, outputs=predictions)

    checkpoint = callback.model_checkpoint(model_type = 'VGG19')
    learning_reducer = callback.learning_reducer()
    early_stop = callback.early_stopping()

    compiled_model = callback.model_compiler(model_final)
    
    trained_model = compiled_model.fit(
        train_set,
        epochs = data_preprocessor.EPOCHS,
        steps_per_epoch = train_set.samples // data_preprocessor.BATCH_SIZE,
        batch_size = data_preprocessor.batch_size,

        validation_data = test_set,
        validation_steps = test_set.samples // data_preprocessor.BATCH_SIZE - 10,
        callback = [checkpoint, learning_reducer, early_stop]
    )
    return trained_model

