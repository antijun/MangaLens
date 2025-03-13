# core.py (in SickZil-Machine/src/core.py)
import os
import consts
import tensorflow as tf
import numpy as np
import utils.imutils as iu
import utils.fp as fp

os.environ['TF_CPP_MIN_LOG_LEVEL'] = consts.TF_CPP_MIN_LOG_LEVEL

# ------------------------------------------------------------------
# SINGLE GLOBAL SESSION (No 'with Session()' calls for segmap/inpaint)
# ------------------------------------------------------------------
_global_sess = None   # Our single TF session
_snet_in = None
_snet_out = None
_cnet_in = None
_cnet_out = None

# For big images
seg_limit = 4000000
compl_limit = 657666

def set_limits(slimit, climit):
    global seg_limit, compl_limit
    seg_limit = slimit
    compl_limit = climit

def init_global_session():
    """
    Creates exactly one global session and imports both SNET and CNET models
    with no prefix. That way, we can reference 'input_1:0'.
    """
    global _global_sess, _snet_in, _snet_out, _cnet_in, _cnet_out
    if _global_sess is not None:
        return  # Already initialized

    print("DEBUG: Initializing global TF session in core.py")
    _global_sess = tf.compat.v1.Session()

    # Force model_name to return no prefix
    def no_prefix(mpath, version):
        return ''
    consts.model_name = no_prefix

    # --- Import the segmentation model into this session ---
    with _global_sess.graph.as_default():
        graph_def = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(consts.SNETPATH, 'rb') as f:
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, name='')  # no prefix
    # Now we can resolve snet_in, snet_out
    _snet_in  = consts.snet_in('0.1.0', _global_sess)
    _snet_out = consts.snet_out('0.1.0', _global_sess)

    # --- Import the completion model into the same session ---
    with _global_sess.graph.as_default():
        graph_def2 = tf.compat.v1.GraphDef()
        with tf.io.gfile.GFile(consts.CNETPATH, 'rb') as f:
            graph_def2.ParseFromString(f.read())
            tf.import_graph_def(graph_def2, name='')  # no prefix
    # Now we can resolve cnet_in, cnet_out
    _cnet_in  = consts.cnet_in('0.1.0', _global_sess)
    _cnet_out = consts.cnet_out('0.1.0', _global_sess)

    # Optional: print out all ops to confirm we have "input_1"
    ops = [op.name for op in _global_sess.graph.get_operations()]
    print("DEBUG: All ops in the global graph:")
    for name in ops:
        print(" ", name)
    print("DEBUG: End of ops list")


# -------------------------------------------------------------------------
# SEGMENTATION
# -------------------------------------------------------------------------
def segment_or_oom(segnet, inp, modulo=16):
    """If image is too big, return None."""
    h, w = inp.shape[:2]
    img = iu.modulo_padded(inp, modulo)
    img_bat = np.expand_dims(img, 0)
    segmap_result = segnet(img_bat)  # calls sess.run(...)
    segmap_result = np.squeeze(segmap_result[:,:h,:w,:], 0)
    return segmap_result

def segment(segnet, inp, modulo=16):
    """Segment the image. If too large, split it."""
    global seg_limit
    h, w = inp.shape[:2]
    result = None
    if h*w < seg_limit:
        result = segment_or_oom(segnet, inp, modulo)
        if result is None:
            seg_limit = h*w
    if result is None:  # fallback if OOM
        if h > w:
            upper  = segment(segnet, inp[:h//2,:], modulo)
            lower  = segment(segnet, inp[h//2:,:], modulo)
            return np.concatenate((upper, lower), axis=0)
        else:
            left  = segment(segnet, inp[:,:w//2], modulo)
            right = segment(segnet, inp[:,w//2:], modulo)
            return np.concatenate((left, right), axis=1)
    return result

def segmap(image):
    """
    Returns a uint8 mask image (background=black).
    If 'image' is not float32 or 3 channels, convert it.
    """
    init_global_session()  # ensure the single session is ready

    def assert_img_range(img):
        # Must be [0..1] for the net
        assert (img >= 0.0).all(), img.min()
        assert (img <= 1.0).all(), img.max()
        return img

    def decategorize(mask):
        return iu.decategorize(mask, iu.rgb2wk_map)

    # snet is a local function that calls sess.run(_snet_out, feed_dict=...)
    def snet(img_bat):
        return _global_sess.run(_snet_out, feed_dict={_snet_in: img_bat})

    return fp.go(
        image,
        iu.channel3img, iu.float32,
        assert_img_range,
        lambda img: segment(snet, img),
        iu.map_max_row, decategorize, iu.uint8
    )

# -------------------------------------------------------------------------
# COMPLETION / INPAINTING
# -------------------------------------------------------------------------
def inpaint_or_oom(complnet, image, segmap):
    """If image is too big, return None."""
    assert image.shape == segmap.shape
    h, w = image.shape[:2]

    image = iu.modulo_padded(image, 8)
    segmap = iu.modulo_padded(segmap, 8)

    image = np.expand_dims(image, 0)
    segmap = np.expand_dims(segmap, 0)
    input_image = np.concatenate([image, segmap], axis=2)

    return complnet(input_image)[0][:h, :w, ::-1]

def inpaint(complnet, img, mask):
    global compl_limit
    h, w = img.shape[:2]
    result = None
    if h*w < compl_limit:
        result = inpaint_or_oom(complnet, img, mask)
        if result is None:
            compl_limit = h*w
    if result is None:
        if h > w:
            top    = inpaint(complnet, img[:h//2,:], mask[:h//2,:])
            bottom = inpaint(complnet, img[h//2:,:], mask[h//2:,:])
            return np.concatenate((top, bottom), axis=0)
        else:
            left  = inpaint(complnet, img[:,:w//2], mask[:,:w//2])
            right = inpaint(complnet, img[:,w//2:], mask[:,w//2:])
            return np.concatenate((left, right), axis=1)
    return result

def inpainted(image, segmap):
    """
    Return a uint8 text-removed image.
    'image':  BGR, uint8
    'segmap': BGR, uint8 (black=bg)
    """
    init_global_session()

    def cnet(img_bat):
        return _global_sess.run(_cnet_out, feed_dict={_cnet_in: img_bat})

    return inpaint(cnet, image, segmap)
