import io

import flask
import numpy as np
from PIL import Image as PILImage

from iris.project import project

main_app = flask.Blueprint(
    'main', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_app.route('/')
def index():
    return flask.redirect(
        flask.url_for('segmentation.index')
    )

@main_app.route('/image/<image_id>/<int:view>')
def load_image(image_id, view):
    image = project.get_image(image_id, project['views'][view]['content'])
    return array_to_png(image)

@main_app.route('/metadata/<image_id>', methods=['GET'])
def load_metadata(image_id):
    metadata = project.get_metadata(image_id)

    if metadata is None:
        return flask.make_response("No metadata found!", 404)

    if flask.request.args.get('safe_html', False):
        metadata = {
            k: flask.Markup(str(v))
            for k, v in metadata.items()
        }

    return flask.jsonify(metadata)

@main_app.route('/thumbnail/<image_id>')
def load_thumbnail(image_id):
    array = project.get_thumbnail(image_id)
    return array_to_png(array)

def array_to_png(array):
    if issubclass(array.dtype.type, np.floating):
        array = np.clip(array * 255., 0, 255).astype('uint8')

    img = PILImage.fromarray(array) # convert arr to image
    file_object = io.BytesIO()   # create file in memory
    img.save(file_object, 'PNG') # save PNG in file in memory
    file_object.seek(0)          # move to beginning of file
    return flask.send_file(file_object,  mimetype='image/png')
