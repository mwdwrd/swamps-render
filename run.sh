dir="input/"
file="*.png"

for file in `cd ${dir};ls -1 ${file}` ;do
   echo "Processing $file..."
   artwork=${file%%.*}

   # python3 ./src/engine.py -a "$artwork"

   blender -b \
      -P src/main.py \
      -E CYCLES \
      -- \
      --artwork "$artwork" \
      --cycles-device CUDA

   # open ./output/$artwork/$artwork.blend
done 
