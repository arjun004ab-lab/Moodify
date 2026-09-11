import io,cv2,numpy as np
from PIL import Image
def scan_beauty(data:bytes):
    if not data:raise ValueError("Empty image.")
    rgb=np.asarray(Image.open(io.BytesIO(data)).convert("RGB"));gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    brightness=float(np.mean(gray)/255*100)
    red=rgb[:,:,0].astype(np.float32);green=rgb[:,:,1].astype(np.float32)
    redness=float(np.clip(np.mean(np.maximum(red-green,0))/255*180,0,100))
    texture=float(np.clip(100-np.std(gray)*1.55,0,100))
    flip=np.fliplr(gray);err=np.mean(np.abs(gray.astype(np.float32)-flip.astype(np.float32)))/255;symmetry=float(np.clip(100-err*220,0,100))
    hydration=float(np.clip(55+(brightness-50)*.45-max(0,redness-25)*.15,0,100))
    pigmentation=float(np.clip(100-np.std(hsv[:,:,1])*2,0,100))
    overall=round(.24*hydration+.18*(100-redness)+.20*texture+.16*symmetry+.14*pigmentation+.08*brightness,1)
    concerns={"redness":redness,"dryness / hydration":100-hydration,"texture":100-texture,"pigmentation":100-pigmentation}
    return {"success":True,"overall_score":overall,"scores":{"skin_hydration":round(hydration,1),"redness":round(redness,1),"skin_texture":round(texture,1),"facial_symmetry":round(symmetry,1),"pigmentation":round(pigmentation,1),"visual_brightness":round(brightness,1)},"primary_beauty_concern":max(concerns,key=concerns.get),"note":"Image-derived visual proxy only—not a medical or dermatological diagnosis. Results can change with lighting, camera quality, pose and composition."}
