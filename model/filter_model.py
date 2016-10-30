import numpy as np
import matplotlib.pyplot as plt
import os
from keras import backend as K

image_path = "./static/upload/"
def compute_activation(model, layer_id, out_path, size=(224, 224)):
    if os.path.exists(out_path + "ok"):
        return
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    layer = model.layers[layer_id]
    im_width, im_height = model.input_shape[2:4] if model.input_shape[2] and model.input_shape[3] else size

    def deprocess_image(x):
        x -= x.mean()
        x /= (x.std() + 1e-5)
        x *= 0.1
        x += 0.5
        x = np.clip(x, 0, 1)
        x *= 255
        x = x.transpose((1, 2, 0))
        x = np.clip(x, 0, 255).astype('uint8')
        return x

    input_img = model.input

    def normalize(x):
        return x / (K.sqrt(K.mean(K.square(x))) + 1e-5)

    filters = []
    for filter_index in range(layer.nb_filter):
        layer_output = layer.output
        loss = K.mean(layer_output[:, filter_index, :, :])
        grads = K.gradients(loss, input_img)[0]
        grads = normalize(grads)

        iterate = K.function([input_img], [loss, grads])
        step = 1.
        input_img_data = np.random.random((1, 3, im_width, im_height))

        for i in range(20):
            loss_value, grads_value = iterate([input_img_data])
            input_img_data += grads_value * step
            print('Current loss value:', loss_value)

        img = deprocess_image(input_img_data[0])
        filters.append((img, loss_value))
        print('Filter %d processed' % (filter_index))
    for i in range(len(filters)):
        plt.imsave(out_path + str(i + 1) + ".png", filters[i][0])
    with open(out_path + "ok", 'w') as f:
        f.write("ok")
