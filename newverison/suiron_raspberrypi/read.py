from suiron import get_servo_dataset
from PIL import Image
import sys

c_x, c_servo = get_servo_dataset('data/output_{}.csv'.format(sys.argv[1]), conf='/Users/bai/tmp/beaglecar/picar_thread/settings.json')
bb=c_x[int(sys.argv[2])]
print(bb.shape)
im=Image.fromarray(bb)
im.save('test.jpg')
