
#This is shader for simple pinhole camera
#Input argument to shader is sample structure that
#hold sample point on image plane
#Shader must calcualte origin and direction of ray

direction = u * sample.x + v * sample.y - w * distance
ray.origin = eye
ray.direction =  normalize(direction)
