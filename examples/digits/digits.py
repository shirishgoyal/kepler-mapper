import io
import sys
import base64

import numpy as np
import sklearn
from sklearn import datasets
import kmapper as km

try:
    from scipy.misc import imsave, toimage
except ImportError as e:
    print("imsave requires you to install pillow. Run `pip install pillow` and then try again.")
    sys.exit()


# Load digits dat
data, labels = datasets.load_digits().data, datasets.load_digits().target

# Create images for a custom tooltip array
tooltip_s = []
for image_data in data:
    output = io.BytesIO()
    img = toimage(image_data.reshape((8,8))) # Data was a flat row of 64 "pixels".
    img.save(output, format="PNG")
    contents = output.getvalue()
    img_encoded = base64.b64encode(contents)
    img_tag = """<img src="data:image/png;base64,{}"> """.format(img_encoded.decode('utf-8'))
    tooltip_s.append(img_tag)
    output.close()

tooltip_s = np.array(tooltip_s) # need to make sure to feed it as a NumPy array, not a list

# Initialize to use t-SNE with 2 components (reduces data to 2 dimensions). Also note high overlap_percentage.
mapper = km.KeplerMapper(verbose=2)

# Fit and transform data
projected_data = mapper.fit_transform(data,
                                      projection=sklearn.manifold.TSNE())

# Create the graph (we cluster on the projected data and suffer projection loss)
graph = mapper.map(projected_data,
                   clusterer=sklearn.cluster.DBSCAN(eps=0.3, min_samples=15),
                   nr_cubes=35,
                   overlap_perc=0.9)

# Create the visualizations (increased the graph_gravity for a tighter graph-look.)

# Tooltips with image data for every cluster member
mapper.visualize(graph,
                 path_html="keplermapper_digits_custom_tooltips.html",
                 graph_gravity=0.25,
                 custom_tooltips=tooltip_s)
# Tooltips with the target y-labels for every cluster member
mapper.visualize(graph,
                 path_html="keplermapper_digits_ylabel_tooltips.html",
                 graph_gravity=0.25,
                 custom_tooltips=labels)
