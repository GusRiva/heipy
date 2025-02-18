# bash
# This scripts compared the xslt templates in the pipelines 1 and 2

dir1="/home/gustavo/Dokumente/heieditionspipeline2/heieditionspipeline/templates/"
dir2="/home/gustavo/Dokumente/Editionen/heiEditionsPipeline/transformations/"

# Loop over all files in dir1
for file in "$dir1"/*; do
  # Check if $file is a regular file (not a directory or anything else)
  if [ -f "$file" ]; then
    # Extract the base filename (just the filename, not the full path)
    filename=$(basename "$file")

    # Check if a file with the same name exists in dir2
    if [ -f "$dir2/$filename" ]; then
      # Compare the two files
      diff "$file" "$dir2/$filename" > /dev/null
      diff_output=$(diff "$file" "$dir2/$filename")
      if [ $? -eq 0 ]; then
        continue
      else
        echo "$diff_output" > "diff_$filename"
        echo "Files '$filename' are different."
      fi
    # else
    #   echo "File '$filename' does not exist in $dir2."
    fi
  fi
done
